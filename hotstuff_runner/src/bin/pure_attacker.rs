use std::collections::HashMap;
use std::env;
use std::error::Error;
use std::net::SocketAddr;
use std::sync::{
    atomic::{AtomicU64, Ordering},
    Arc,
};
use std::time::{Duration, Instant};

use crossbeam::queue::SegQueue;
use dashmap::DashSet;
use ed25519_dalek::SigningKey;
use hotstuff_rs::types::{
    crypto_primitives::VerifyingKey,
    data_types::Power,
    update_sets::{AppStateUpdates, ValidatorSetUpdates},
};
use hotstuff_runner::event::{SystemEvent, TestTransaction};
use hotstuff_runner::pompe::{load_pompe_config, PompeMessage, PompeTransaction};
use hotstuff_runner::pompe_network::PompeNetwork;
use hotstuff_runner::smrol::{
    message::{SmrolMessage, SmrolTransaction},
    network::SmrolTcpNetwork,
};
use hotstuff_runner::stats::PerformanceStats;
use hotstuff_runner::tcp_node::Node;
use hotstuff_runner::tokio_network::{TokioNetwork, TokioNetworkConfig};
use rand::Rng;
use sha2::{Digest, Sha256};
use tokio::io::AsyncReadExt;
use tokio::net::{lookup_host, TcpListener};
use tokio::sync::broadcast;
use tokio::time::sleep;
use tracing::{info, warn};

type DynError = Box<dyn Error + Send + Sync>;

const CLIENT_MAX_MESSAGE_BYTES: usize = 12 * 1024 * 1024;

#[tokio::main]
async fn main() -> Result<(), DynError> {
    setup_logging();

    let protocol = env::var("ADVERSARY_MODE")
        .or_else(|_| env::var("ATTACK_PROTOCOL"))
        .unwrap_or_else(|_| "pompe".to_string())
        .to_lowercase();

    let node_id = env::var("NODE_ID")
        .unwrap_or_else(|_| "1".to_string())
        .parse::<usize>()?;
    let node_least_id = env::var("NODE_LEAST_ID")
        .unwrap_or_else(|_| "1".to_string())
        .parse::<usize>()?;
    let node_num = env::var("NODE_NUM")
        .unwrap_or_else(|_| "4".to_string())
        .parse::<usize>()?;

    let hosts = parse_node_hosts()?;
    let ids: Vec<usize> = (node_least_id..node_least_id + node_num).collect();
    let sleep_micros = env::var("ATTACK_SLEEP_MICROS")
        .ok()
        .and_then(|v| v.parse::<u64>().ok());
    let attack_start_delay_ms = env::var("ATTACK_START_DELAY_MS")
        .ok()
        .and_then(|v| v.parse::<u64>().ok())
        .unwrap_or(22_000);
    let hotstuff_start_delay_secs = env::var("HOTSTUFF_START_DELAY_SECS")
        .ok()
        .and_then(|v| v.parse::<u64>().ok())
        .unwrap_or(20);

    if protocol != "pompe" && protocol != "smrol" {
        return Err(format!(
            "Unknown ATTACK_PROTOCOL '{}'; expected pompe or smrol",
            protocol
        )
        .into());
    }

    // Start the normal HotStuff transport immediately so peers can connect to node1.
    // The ordering attack remains a separate path and never enters this queue.
    let signing_key = SigningKey::from_bytes(&[(node_id + 1) as u8; 32]);
    let my_verifying_key = VerifyingKey::from(signing_key.verifying_key());
    let mut peer_addrs = HashMap::new();
    let mut validator_set_updates = ValidatorSetUpdates::new();

    for id in &ids {
        let peer_signing_key = SigningKey::from_bytes(&[(*id + 1) as u8; 32]);
        let peer_verifying_key = VerifyingKey::from(peer_signing_key.verifying_key());
        let addr = resolve_node_addr(&hosts, *id, 10_000, "HotStuff").await?;
        peer_addrs.insert(peer_verifying_key, addr);
        validator_set_updates.insert(peer_verifying_key, Power::new(1));
    }

    if !peer_addrs.contains_key(&my_verifying_key) {
        return Err(format!(
            "Attacker node {} is not in the HotStuff validator set",
            node_id
        )
        .into());
    }

    let my_port = env::var("NODE_PORT")
        .unwrap_or_else(|_| "10000".to_string())
        .parse::<u16>()?;

    // Keep the Byzantine replica reachable through the same client endpoint as
    // every honest replica.  It deliberately consumes and discards client
    // requests without producing ordering/consensus acknowledgements.
    let client_port = my_port
        .checked_sub(1000)
        .ok_or("NODE_PORT must be at least 1000")?;
    let client_addr = format!("0.0.0.0:{}", client_port);
    let client_listener = TcpListener::bind(&client_addr).await.map_err(|e| {
        format!(
            "Failed to bind attacker client listener on {}: {}",
            client_addr, e
        )
    })?;
    warn!(
        "[attacker-client-sink] node {} accepting and discarding client requests on {}",
        node_id, client_addr
    );
    tokio::spawn(run_client_sink(node_id, client_listener));

    let hotstuff_network = TokioNetwork::new(TokioNetworkConfig {
        my_addr: format!("0.0.0.0:{}", my_port).parse()?,
        peer_addrs,
        my_key: my_verifying_key,
    })
    .map_err(|e| format!("Failed to start attacker HotStuff network: {}", e))?;

    let attack_protocol = protocol.clone();
    let attack_ids = ids.clone();
    let attack_hosts = hosts.clone();
    let attack_task = tokio::spawn(async move {
        sleep(Duration::from_millis(attack_start_delay_ms)).await;
        match attack_protocol.as_str() {
            "pompe" => {
                warn!("🚀 Starting Pompe pure attacker (node {})", node_id);
                run_pompe_attacker(node_id, &attack_ids, &attack_hosts, sleep_micros).await
            }
            "smrol" => {
                warn!("🚀 Starting SMROL pure attacker (node {})", node_id);
                run_smrol_attacker(node_id, &attack_ids, &attack_hosts, sleep_micros).await
            }
            _ => unreachable!("attack protocol was validated before spawning"),
        }
    });

    // Match docker_node's startup delay so all four replicas enter HotStuff together.
    sleep(Duration::from_secs(hotstuff_start_delay_secs)).await;
    let hotstuff_queue = Arc::new(SegQueue::new());
    let confirmed_txs = Arc::new(DashSet::new());
    let in_flight_txs = Arc::new(DashSet::new());
    let stats = Arc::new(PerformanceStats::new());
    let (event_tx, _event_rx) = broadcast::channel::<SystemEvent>(2_000);
    let _hotstuff_node = Node::new(
        node_id,
        signing_key,
        hotstuff_network,
        AppStateUpdates::new(),
        validator_set_updates,
        hotstuff_queue,
        stats,
        event_tx,
        confirmed_txs,
        in_flight_txs,
    );
    warn!(
        "✅ Pure attacker node {} is participating in HotStuff; attack traffic remains ordering-only",
        node_id
    );

    attack_task.await??;
    Ok(())
}

async fn run_client_sink(node_id: usize, listener: TcpListener) {
    loop {
        let (mut socket, peer_addr) = match listener.accept().await {
            Ok(connection) => connection,
            Err(err) => {
                warn!(
                    "[attacker-client-sink] node {} failed to accept a client connection: {}",
                    node_id, err
                );
                continue;
            }
        };

        tokio::spawn(async move {
            let mut length_buf = [0u8; 4];
            let mut discarded = 0u64;

            loop {
                if socket.read_exact(&mut length_buf).await.is_err() {
                    break;
                }

                let message_length = u32::from_be_bytes(length_buf) as usize;
                if message_length > CLIENT_MAX_MESSAGE_BYTES {
                    warn!(
                        "[attacker-client-sink] node {} closing {} after oversized client message ({} bytes)",
                        node_id, peer_addr, message_length
                    );
                    break;
                }

                let mut message = vec![0u8; message_length];
                if socket.read_exact(&mut message).await.is_err() {
                    break;
                }
                discarded += 1;
            }

            info!(
                "[attacker-client-sink] node {} client {} disconnected; discarded {} requests",
                node_id, peer_addr, discarded
            );
        });
    }
}

async fn run_pompe_attacker(
    node_id: usize,
    node_ids: &[usize],
    _hosts: &HashMap<String, String>,
    sleep_micros: Option<u64>,
) -> Result<(), DynError> {
    let worker_count = env::var("POMPE_ATTACK_WORKERS")
        .ok()
        .and_then(|v| v.parse::<usize>().ok())
        .unwrap_or(1)
        .max(1);
    let report_interval_secs = env::var("ATTACK_REPORT_INTERVAL_SECS")
        .ok()
        .and_then(|v| v.parse::<u64>().ok())
        .unwrap_or(10)
        .max(1);
    let network = Arc::new(PompeNetwork::new(node_id, node_ids.to_vec()));
    network
        .start_server()
        .map_err(|e| format!("Failed to start Pompe attacker listener: {}", e))?;

    // Match the paper's attack model: honest replicas send their timestamp
    // responses back to the Byzantine initiator, which receives and discards
    // them without advancing the ordering protocol.
    let successful_broadcasts = Arc::new(AtomicU64::new(0));
    let failed_broadcasts = Arc::new(AtomicU64::new(0));
    let discarded_responses = Arc::new(AtomicU64::new(0));
    let discarded_other_messages = Arc::new(AtomicU64::new(0));

    let response_network = Arc::clone(&network);
    let response_counter = Arc::clone(&discarded_responses);
    let other_counter = Arc::clone(&discarded_other_messages);
    network.spawn(async move {
        while let Some((_from_node_id, message)) = response_network.recv().await {
            match message {
                PompeMessage::Ordering1Response { .. } => {
                    response_counter.fetch_add(1, Ordering::Relaxed);
                }
                _ => {
                    other_counter.fetch_add(1, Ordering::Relaxed);
                }
            }
        }
    });
    warn!(
        "[pompe-attacker] listening for honest ordering responses and discarding them; workers={}, sleep={} us",
        worker_count,
        sleep_micros.unwrap_or(0)
    );

    let report_network = Arc::clone(&network);
    let report_successful = Arc::clone(&successful_broadcasts);
    let report_failed = Arc::clone(&failed_broadcasts);
    let report_responses = Arc::clone(&discarded_responses);
    let report_other = Arc::clone(&discarded_other_messages);
    let honest_peer_count = node_ids.iter().filter(|&&id| id != node_id).count().max(1);
    network.spawn(async move {
        let mut ticker = tokio::time::interval(Duration::from_secs(report_interval_secs));
        ticker.tick().await;
        let mut previous_successful = 0u64;
        let mut previous_responses = 0u64;
        let mut previous_report = Instant::now();

        loop {
            ticker.tick().await;
            let now = Instant::now();
            let elapsed = now.duration_since(previous_report).as_secs_f64().max(0.001);
            let successful = report_successful.load(Ordering::Relaxed);
            let failed = report_failed.load(Ordering::Relaxed);
            let responses = report_responses.load(Ordering::Relaxed);
            let other = report_other.load(Ordering::Relaxed);
            let broadcast_rate = successful.saturating_sub(previous_successful) as f64 / elapsed;
            let response_rate = responses.saturating_sub(previous_responses) as f64 / elapsed;
            let per_honest_rate = response_rate / honest_peer_count as f64;

            warn!(
                "[pompe-attacker][rate] broadcasts={:.1}/s, responses={:.1}/s (~{:.1} requests/s per honest node), totals: broadcasts={}, failed={}, responses={}, other={}, queue_drops={}",
                broadcast_rate,
                response_rate,
                per_honest_rate,
                successful,
                failed,
                responses,
                other,
                report_network.queue_saturation_drops()
            );

            previous_successful = successful;
            previous_responses = responses;
            previous_report = now;
        }
    });

    // start_server binds on the dedicated Pompe runtime; give it a brief
    // scheduling window before the first flooding request is broadcast.
    sleep(Duration::from_millis(100)).await;

    let batch_size = load_pompe_config().batch_size;
    let next_tx_id = Arc::new(AtomicU64::new(1_000_001));
    let mut workers = Vec::with_capacity(worker_count);

    for worker_id in 0..worker_count {
        let worker_network = Arc::clone(&network);
        let worker_next_tx_id = Arc::clone(&next_tx_id);
        let worker_successful = Arc::clone(&successful_broadcasts);
        let worker_failed = Arc::clone(&failed_broadcasts);
        workers.push(tokio::spawn(async move {
            if worker_id > 0 {
                sleep(Duration::from_millis((worker_id as u64) * 25)).await;
            }
            run_pompe_flood_worker(
                node_id,
                worker_id,
                batch_size,
                worker_network,
                sleep_micros,
                worker_next_tx_id,
                worker_successful,
                worker_failed,
            )
            .await;
        }));
    }

    workers
        .remove(0)
        .await
        .map_err(|e| format!("Pompe attack worker terminated: {}", e))?;
    Err("Pompe attack worker exited unexpectedly".into())
}

async fn run_pompe_flood_worker(
    node_id: usize,
    worker_id: usize,
    batch_size: usize,
    network: Arc<PompeNetwork>,
    sleep_micros: Option<u64>,
    next_tx_id: Arc<AtomicU64>,
    successful_broadcasts: Arc<AtomicU64>,
    failed_broadcasts: Arc<AtomicU64>,
) {
    let mut generator = TransactionGenerator::new();

    loop {
        let mut tx = generator.generate_transaction();
        tx.id = next_tx_id.fetch_add(1, Ordering::Relaxed);
        let pompe_tx = PompeTransaction {
            id: tx.id,
            from: tx.from.clone(),
            to: tx.to.clone(),
            amount: tx.amount,
            client_id: format!("attacker_{}_worker_{}", node_id, worker_id),
            timestamp: tx.timestamp,
            nonce: tx.nonce,
        };
        let tx_hash = pompe_tx.hash();

        let msg = PompeMessage::Ordering1Request {
            tx_hash,
            transaction: pompe_tx,
            batch_size,
            initiator_node_id: node_id,
        };

        match network.broadcast_skip_self(msg).await {
            Ok(()) => {
                successful_broadcasts.fetch_add(1, Ordering::Relaxed);
            }
            Err(e) => {
                let failures = failed_broadcasts.fetch_add(1, Ordering::Relaxed) + 1;
                if failures == 1 || failures % 1_000 == 0 {
                    warn!(
                        "[pompe-attacker] broadcast failures={} (latest: {})",
                        failures, e
                    );
                }
            }
        }

        if let Some(us) = sleep_micros {
            sleep(Duration::from_micros(us)).await;
        }
    }
}

async fn run_smrol_attacker(
    node_id: usize,
    node_ids: &[usize],
    hosts: &HashMap<String, String>,
    sleep_micros: Option<u64>,
) -> Result<(), DynError> {
    let mut peer_addrs = HashMap::new();
    for id in node_ids {
        let port = 21000 + *id as u16;
        let addr = resolve_node_addr(hosts, *id, port, "SMROL").await?;
        peer_addrs.insert(*id, addr);
    }

    let network = Arc::new(SmrolTcpNetwork::new(node_id, peer_addrs));
    let mut generator = TransactionGenerator::new();
    let mut sent: u64 = 0;

    loop {
        let tx = generator.generate_transaction();
        let smrol_tx =
            SmrolTransaction::from_test_transaction(tx.clone(), format!("attacker_{}", node_id));
        // Keep the deliberately non-contiguous sequence-number attack. Creating
        // the thread-local RNG inside this expression also keeps the attack task Send.
        let sequence = rand::thread_rng().gen_range(0u64, 1_000_000_000u64);
        let mut hasher = Sha256::new();
        hasher.update(tx.id.to_le_bytes());
        hasher.update(tx.from.as_bytes());
        hasher.update(tx.to.as_bytes());
        hasher.update(tx.amount.to_le_bytes());
        hasher.update(sequence.to_le_bytes());
        let tx_hash = format!("{:x}", hasher.finalize());

        let message = SmrolMessage::SeqRequest {
            tx_hash,
            transaction: smrol_tx,
            sender_id: node_id,
            sequence_number: sequence,
        };

        if let Err(e) = network.broadcast_skip_self(message).await {
            warn!("[smrol-attacker] broadcast failed: {}", e);
        }

        sent += 1;
        if sent % 10_000 == 0 {
            info!("[smrol-attacker] sent {} requests", sent);
        }

        if let Some(us) = sleep_micros {
            sleep(Duration::from_micros(us)).await;
        }
    }
}

async fn resolve_node_addr(
    hosts: &HashMap<String, String>,
    node_id: usize,
    port: u16,
    network_name: &str,
) -> Result<SocketAddr, DynError> {
    let key = format!("node{}", node_id);
    let host = hosts
        .get(&key)
        .ok_or_else(|| format!("Missing host entry for {}", key))?;
    let resolved = lookup_host((host.as_str(), port))
        .await
        .map_err(|e| {
            format!(
                "Failed to resolve {} peer {} ({}:{}): {}",
                network_name, key, host, port, e
            )
        })?
        .collect::<Vec<SocketAddr>>();
    let addr = resolved
        .iter()
        .copied()
        .find(SocketAddr::is_ipv4)
        .or_else(|| resolved.first().copied())
        .ok_or_else(|| {
            format!(
                "{} peer {} ({}:{}) resolved to no addresses",
                network_name, key, host, port
            )
        })?;
    info!(
        "[pure-attacker] resolved {} peer {} ({}:{}) to {}",
        network_name, key, host, port, addr
    );
    Ok(addr)
}

fn parse_node_hosts() -> Result<HashMap<String, String>, DynError> {
    let hosts = env::var("NODE_HOSTS")
        .map_err(|_| "NODE_HOSTS env var is required (format: node0:1.2.3.4,node1:5.6.7.8)")?;
    let map = hosts
        .split(',')
        .filter_map(|entry| {
            let mut parts = entry.split(':');
            let name = parts.next()?.trim().to_string();
            let ip = parts.next()?.trim().to_string();
            Some((name, ip))
        })
        .collect::<HashMap<_, _>>();
    Ok(map)
}

fn setup_logging() {
    let _ = tracing_subscriber::fmt()
        .with_env_filter(tracing_subscriber::EnvFilter::from_default_env())
        .with_target(false)
        .try_init();
}

struct TransactionGenerator {
    current_tx_id: u64,
    current_nonce: u64,
    accounts: Vec<String>,
    large_payload: Option<String>,
}

impl TransactionGenerator {
    fn new() -> Self {
        let accounts = vec![
            "alice".to_string(),
            "bob".to_string(),
            "charlie".to_string(),
            "david".to_string(),
            "eve".to_string(),
        ];
        let payload_bytes = env::var("ADVERSARY_PAYLOAD_BYTES")
            .ok()
            .and_then(|raw| raw.trim().parse::<usize>().ok())
            .filter(|size| *size > 0);
        let large_payload = payload_bytes.map(|size| {
            let mut payload = String::with_capacity(size);
            while payload.len() < size {
                let remaining = size - payload.len();
                let chunk = remaining.min(1024);
                payload.push_str(&"X".repeat(chunk));
            }
            payload
        });
        Self {
            current_tx_id: 0,
            current_nonce: 0,
            accounts,
            large_payload,
        }
    }

    fn generate_transaction(&mut self) -> TestTransaction {
        let mut rng = rand::thread_rng();
        let (from, to) = if let Some(payload) = &self.large_payload {
            let mut from_payload = payload.clone();
            from_payload.push_str(&format!("-{}", self.current_tx_id));
            (from_payload, payload.clone())
        } else {
            let from_idx = rng.gen_range(0, self.accounts.len());
            let mut to_idx = rng.gen_range(0, self.accounts.len());
            while to_idx == from_idx {
                to_idx = rng.gen_range(0, self.accounts.len());
            }
            (
                self.accounts[from_idx].clone(),
                self.accounts[to_idx].clone(),
            )
        };
        let amount = rng.gen_range(1, 100000);
        self.current_tx_id += 1;
        self.current_nonce += 1;
        TestTransaction {
            id: rng.gen_range(100_0001u64, 3_000_001u64),
            from,
            to,
            amount,
            timestamp: std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_secs(),
            nonce: self.current_nonce,
        }
    }
}
