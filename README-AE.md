# SMR-OL Artifact Evaluation Guide

## Abstract

This document provides the instructions for evaluating the artifact associated
with the following paper:

> **Isotaxis: Optimal Asynchronous Byzantine Consensus with Ordering Linearizability**  
> Network and Distributed System Security Symposium (NDSS 2027)

This artifact accompanies Isotaxis: Optimal Asynchronous Byzantine Consensus with Ordering Linearizability. Isotaxis is a state machine replication (SMR) protocol that provides ordering linearizability in asynchronous networks while achieving optimal Byzantine resilience, standard liveness, and communication complexity $O(n\ell+\lambda n^2)$, which is optimal when $\ell \geq \lambda n$. The artifact contains the Rust implementation of Isotaxis, a Rust implementation of Pompe used as the baseline, and a common HotStuff consensus backend for a fair comparison. It provides Docker configurations for a four-replica local functional evaluation, scripts for distributed experiments on Amazon EC2, workload generators, adversarial-node implementations, and tools for collecting and analyzing latency and throughput results. These materials support the paper’s evaluation of Isotaxis and Pompe with 4–100 replicas across 11 AWS regions, including scalability, throughput–latency trade-offs, and robustness against denial-of-service attacks.

The artifact is intended to support the following badges:

- **Artifacts Available:** the evaluated snapshot will be archived at a
  permanent DOI.
- **Artifacts Functional:** evaluators can build the implementation and run a
  four-replica SMR-OL deployment locally.
- **Results Reproduced:** evaluators can analyze the archived raw results and,
  subject to the resource notes below, rerun scaled-down or full experiments.

## Obtain the Artifact

During artifact evaluation, use the latest main commit:

```bash
git clone https://github.com/xrxrxrxrxr/Isotaxis-ArtifactEvaluation.git
cd Isotaxis-ArtifactEvaluation
```

The artifact includes a modified snapshot of `hotstuff_rs` 0.4.0 under
[hotstuff_rs/](hotstuff_rs/). All builds automatically use this bundled version
through the local Cargo path dependency in
[hotstuff_runner/Cargo.toml](hotstuff_runner/Cargo.toml).

The evaluated artifact will be permanently archived at:

- Repository:
  <https://github.com/xrxrxrxrxr/Isotaxis-ArtifactEvaluation.git>


## Artifact Overview

### Components

| Component | Location | Purpose |
|---|---|---|
| SMR-OL/HotStuff runner | [hotstuff_runner/](hotstuff_runner/) | Node, adversarial-node, attacker, and client executables |
| SMR-OL implementation | [hotstuff_runner/src/smrol/](hotstuff_runner/src/smrol/) | Sequencing, finalization, consensus, cryptography, networking, and the PNFIFO component |
| HotStuff library | [hotstuff_rs/](hotstuff_rs/) | Artifact-specific HotStuff source snapshot included directly in this repository |
| Local deployment | [Dockerfile](Dockerfile), [docker-compose.yml](docker-compose.yml), [.env](.env) | Four-replica Docker deployment and workload configuration |
| Distributed deployment | [ec2/](ec2/) | Multi-region EC2 plans, deployment scripts, and per-node configuration generation |
| Baseline implementation | [pompe.rs](hotstuff_runner/src/pompe.rs), [pompe_network.rs](hotstuff_runner/src/pompe_network.rs), [pompe_adversary.rs](hotstuff_runner/src/pompe_adversary.rs) | Pompe-HS comparison and adversarial-mode implementation included in the runner |
| Result processing | [gen-fig.py](gen-fig.py) | Parser and plotter for paper figures |


### Executables

The main executables are:

| Executable | Source | Role |
|---|---|---|
| `docker_node` | [hotstuff_runner/src/bin/docker_node.rs](hotstuff_runner/src/bin/docker_node.rs) | Regular replica |
| `docker_node_adversary` | [hotstuff_runner/src/bin/docker_node_adversary.rs](hotstuff_runner/src/bin/docker_node_adversary.rs) | Replica with experiment-specific adversarial behavior |
| `pure_attacker` | [hotstuff_runner/src/bin/pure_attacker.rs](hotstuff_runner/src/bin/pure_attacker.rs) | Standalone attacker used by selected experiments |
| `client` | [hotstuff_runner/src/bin/client.rs](hotstuff_runner/src/bin/client.rs) | Workload generator and latency collector |

### Repository structure

```text
.
├── Dockerfile                    # Multi-stage Rust build and runtime image
├── docker-compose.yml            # Four-replica local deployment
├── docker-compose.attack.yml     # Replaces node1 with the attack-only generator
├── .env                          # Default local experiment configuration
├── .attack.env                   # Local attack-only experiment configuration
├── run_test.sh                   # Existing local orchestration helper
├── hotstuff_runner/
│   └── src/
│       ├── bin/                  # Node, client, and attacker entry points
│       └── smrol/                # SMR-OL implementation
├── hotstuff_rs/                  # Artifact-specific HotStuff source snapshot
├── ec2/
│   ├── plans/                    # Multi-region node-count plans
│   ├── start_instances.sh        # Starts pre-existing stopped instances
│   ├── get_ips.sh                # Discovers instances and generates configuration
│   ├── generate-node-envs.sh     # Generates node/client environment files
│   └── Makefile                  # Deploy, run, collect, and clean workflow
├── gen-fig.py                    # Regenerates paper figures from embedded processed data
└── requirements-plot.txt         # Pinned Python plotting dependency
```

### Software dependencies

The containerized local evaluation requires:

- an x86-64 Linux host;
- Git;
- Docker Engine;
- Docker Compose v2 (`docker compose`);
- Internet access during the first image build to download Rust crates and base
  images.
- Python 3.9 or newer and  package [matplotlib 3.9.4](https://pypi.org/project/matplotlib/3.9.4/), to
  regenerate plots;

Optional dependencies are:

- Rust/Cargo, to build and check the source outside Docker;
- AWS CLI v2, Bash 4 or newer, `jq`, SSH, SCP, and GNU Make, for distributed
  EC2 experiments.


### Hardware requirements

#### Local functionality evaluation

Recommended minimum:

- x86-64 CPU with 8 logical cores;
- 16 GiB RAM;
- 20 GiB free disk space;
- no GPU or specialized hardware.

The CPU-affinity defaults in [.env](.env) refer to cores 0--3. Evaluators using fewer
cores, ARM machines, Docker Desktop, or non-Linux hosts may need to remove or
adjust the `*_CORES` settings. Performance measurements from such environments
must not be compared directly with the paper.

#### Full distributed evaluation

The EC2 scripts currently select pre-existing stopped `c6a.2xlarge` instances
by default and distribute replicas across the regions listed in an experiment
plan. They do not provision new instances from scratch.

Section VIII of the paper reports that every protocol process ran on a
dedicated Amazon EC2 `c6a.2xlarge` instance (8 vCPUs and 16 GB RAM), with one
`t3.micro` instance acting as the client. Experiments used 4--100 processes,
distributed as evenly as possible across 11 AWS regions: North Virginia, North
California, Mumbai, Singapore, Sydney, Tokyo, Montreal, Frankfurt, Dublin,
London, and Sao Paulo. Figure 5 evaluates
`n = 4, 10, 20, 30, 40, 50, 60, 70, 80, 100`; Figure 6 reports `n = 16, 64,
100`; and the denial-of-service experiment in Figure 7 uses `n = 30`.

Workloads vary the batch size up to `1.6 x 10^5` transactions. A batch is
treated as one protocol input and receives one timestamp (Pompe) or sequence
number (Isotaxis); batch size one therefore represents one transaction. The
paper measures latency from client submission until final ordering and reports
the average over 5,000 transactions for Figure 5. Throughput is the number of
committed transactions per second over a fixed window. The paper explicitly
identifies a two-minute run for the `n = 100`, batch-size `1.3 x 10^4` example,
while Figure 7 uses batch size 3 and 3,000 committed transactions.


## Important Safety and Cost Notice

The local evaluation creates Docker images, containers, networks, and log files
on the evaluator's machine. It does not require cloud credentials.

The distributed scripts are **not safe to run without review**:

- [ec2/start_instances.sh](ec2/start_instances.sh) starts billable EC2 instances in multiple regions;
- [ec2/get_ips.sh](ec2/get_ips.sh) records the addresses of running instances
  and generates per-node configuration under the ignored `ec2/envs/` directory;
- `make clean` removes remote `~/hotstuff/logs/*` and stops instances;
- `make clean-ec2` removes the remote `~/hotstuff` directory;
- `make clean-images` performs Docker system pruning on remote hosts;
- the repository does not include an SSH private key; set `SSH_KEY_PATH` to the
  key authorized for the selected instances and, if necessary, set `SSH_USER`;
- [ec2/copy_security_group.sh](ec2/copy_security_group.sh) creates security
  groups and ingress rules from the caller-supplied
  `SOURCE_SECURITY_GROUP_ID`; review the source rules before use.

Always start with `--dry-run`, inspect the selected regions and instances, and
back up required results before invoking a cleanup target. The default AE
evaluation does not require reviewers to run the EC2 workflow unless the
authors explicitly provide credentials or a prepared anonymous environment.

## Evaluation Roadmap

We recommend performing the evaluation in this order:

| ID | Evaluation | Purpose | Expected time |
|---|---|---|---:|
| E0 | Validate package and build | Confirm the snapshot and dependencies are complete | 5--20 minutes |
| E1 | Four-replica local runs | Exercise the normal and adversarial paths end to end | ~ 5 minutes per run (~ 1 hour for full local tests) |
| E2 | Analyze archived paper results | Regenerate reported statistics and plots | ~ 10 seconds |
| E3 | AWS evaluation for Figure 6 | Run the scaled or full-size distributed configuration with the same workflow | Optional; ~ 5 minutes per run, (~ 4.5 hours for full evaluations on AWS) |

The first Docker build may take longer depending on network and crate-cache
state. E0 and E1 target the Functional badge. E2--E3 must be completed and
linked to concrete paper claims before requesting the Reproduced badge.

## E0: Validate the Package and Build

### E0.1 Check the evaluated revision

```bash
git rev-parse HEAD
```

The command should print the evaluated commit listed under
[Obtain the Artifact](#obtain-the-artifact).

### E0.2 Validate Docker Compose

```bash
docker version                
docker compose version
docker compose config --quiet
```
The artifact has been tested with:

- Docker Engine 28.3.2;
- Docker Compose v2.38.2-desktop.1.

The local Docker evaluation uses BuildKit features. A host-side Rust installation is not required.

## E1: Four-Replica Local Evaluation (~ 5 minutes per run)

### E1.1 Normal end-to-end run

Start at the **root folder**. The default [.env](.env) selects four replicas and `CLIENT_ORDERING_MODE=smrol`.
This experiment is a scale-down local simulation of **Fig. 3, 5, 6**.

- **Fig. 5**'s 4-node sparse latency data can be simulated by setting `ORDERING_BATCH_SIZE=1` in [.env](.env).
- **Fig. 3 and 6**'s batched TPS and latency data can be simulated by setting `ORDERING_BATCH_SIZE` to a larger value in [.env](.env), e.g., `1000, 5000, 20000, 50000, ...`.
- *Examples*. Preserved normal-run examples are available under
  [./log-examples/smrol.](log-examples/smrol/) and
  [./log-examples/pompe](log-examples/pompe/). Each directory contains the
  client aggregate-latency log and the per-node HotStuff consensus TPS logs. Some scale up AWS data can be found under [./ec2/logs-data](ec2/logs-data). Note that the full AWS data can be much larger than the local ones as they include round-trip times, typically round 300ms.


### Preparation (~ 10seconds)

Ensure the ports declared in [docker-compose.yml](docker-compose.yml) are free and remove containers
left by an earlier attempt:

```bash
docker compose --profile "*" down
```

<!-- Use info-level logs so the client latency and replica commit summaries are
visible:

```bash
LOG_LEVEL=info docker compose --profile load_test up --build -d
``` -->

### Execution (~ 4 minutes)

Using scripts to automatically **build/rebuild** and **run** local test:
```bash
./run_test.sh           # build/rebuild and run
or
./run_test.sh --reuse   # run without rebuilding
```

Change the mode (protocol) in [.env](.env):
```bash
CLIENT_ORDERING_MODE=smrol    # run SMROL test
or
CLIENT_ORDERING_MODE=pompe    # run Pompe test
```

Modify the batch size in [.env](.env):
```bash
ORDERING_BATCH_SIZE=5000    # For throughput tests (Fig. 6): 1000, 5000, 20000, 50000, ...
ORDERING_BATCH_SIZE=1       # For sparse latency tests (Fig. 5): 1
```


<!-- Wait for the containers to start and the workload to make progress:

```bash
sleep 60
docker compose ps
docker compose logs --no-color load_tester | tail -n 200
docker compose logs --no-color node0 | tail -n 200
```

For a longer unattended run, the existing orchestration helper can be used:

```bash
LOG_LEVEL=info ./run_test.sh load_test --rebuild
``` -->

<!-- The helper includes fixed waits and normally takes more than four minutes in
addition to the first image build. It removes [logs/](logs/) at startup and stops the
cluster at the end. -->

### Expected results

A successful run has all four node containers `hotstuff_node*` and the `hotstuff_load_tester` container
running during the workload. The terminal should show details like:
```
Starting the cluster by reusing existing images...
[+] Running 5/5
 ✔ Container hotstuff_load_tester  Started                                                                        0.6s
 ✔ Container hotstuff_node3        Started                                                                        0.4s
 ✔ Container hotstuff_node1        Started                                                                        0.3s
 ✔ Container hotstuff_node0        Started                                                                        0.4s
 ✔ Container hotstuff_node2        Started                                                                        0.3s
Waiting for nodes to initialize...
Checking node health...
  node 0 is: ✅ running
  node 1 is: ✅ running
  node 2 is: ✅ running
  node 3 is: ✅ running
Checking client health...
  Client (load_tester): running

Cluster startup complete!
```

The cluster will run the test and stop automatically by showing:
```
Stopping the test: docker compose --profile "*" down
- Stops automatically after 2 minutes -
[+] Stopping 5/5
 ✔ Container hotstuff_load_tester  Stopped                                                                        0.3s
 ✔ Container hotstuff_node3        Stopped                                                                       10.8s
 ✔ Container hotstuff_node1        Stopped                                                                       11.0s
 ✔ Container hotstuff_node0        Stopped                                                                       11.5s
 ✔ Container hotstuff_node2        Stopped                                                                       11.2s
 ```

Then results can be found under [logs/](logs/) with a structure of:
```bash
.
├── load_test.log              # client log: aggregate latency repot
├── node
│   ├── consensus-node0.log    # node's consensus log: real-time TPS
│   ├── consensus-node1.log
│   ├── consensus-node2.log
│   └── consensus-node3.log
├── node0.log                  # node's general runtime log
├── node1.log
├── node2.log
└── node3.log
```

This folder will be **auto-cleared** before a new run starts.
The logs should contain evidence of:

- aggregate latency reports in [logs/load_test.log](logs/load_test.log);
- HotStuff committing TPS in the `consensus-node*.log` files under
  [logs/node/](logs/node/).

### E1.2 Local Attack-only test (~ 5 minutes)

This is a scaled-down local version of the DoS attack in **Fig. 2** and checks
the robustness trend reported in **Fig. 7**. At the ordering layer, node1 runs
`pure_attacker`; at the consensus layer, all four nodes still participate in
HotStuff, so the test isolates ordering-layer flooding from a missing-replica
leader timeout.

- **Fig. 2**'s flooding attack is simulated by node1 continuously sending
  adversarial ordering requests while node0, node2, and node3 remain honest.
- **Fig. 7**'s robustness trend is checked by comparing each protocol's local
  attack run with its corresponding normal run. This 4-node test checks the
  qualitative trend rather than reproducing the paper's 30-node values.
- *Examples*. Preserved attack runs are available under `./log-examples/attack-logs`. 

#### Preparation

Preserve the E1.1 normal-run logs because a new run clears [logs/](logs/).

For the Isotaxis attack test, set the following values in
[.attack.env](.attack.env):

```bash
CLIENT_ORDERING_MODE=smrol
ADVERSARY_MODE=smrol
CLIENT_EXCLUDED_NODE_IDS=1
ATTACK_SLEEP_MICROS=100
ATTACK_START_DELAY_MS=2000
ADVERSARY_PAYLOAD_BYTES=500
```

#### Execution

```bash
./run_test.sh adversary --rebuild
```

Use `--reuse` instead of `--rebuild` to repeat a run. To test the
Pompe baseline, set both protocol variables to `pompe`
```bash
CLIENT_ORDERING_MODE=pompe
ADVERSARY_MODE=pompe
POMPE_ATTACK_WORKERS=4
ATTACK_REPORT_INTERVAL_SECS=10
ADVERSARY_PAYLOAD_BYTES=500
```
and run the same command.

`POMPE_ATTACK_WORKERS=4` creates four concurrent sender tasks inside the same
Byzantine node1 process; it does not add Byzantine replicas.

#### Expected results

- node1 reports either `Starting SMROL pure attacker (node 1)` or
  `Starting Pompe pure attacker (node 1)`, followed by
  `Pure attacker node 1 is participating in HotStuff`. In Pompe mode it also
  reports that it is listening for and discarding honest ordering responses;
- in Pompe mode, node1 prints a compact `[pompe-attacker][rate]` line every
  10 seconds. It reports broadcast rate, response rate, the estimated request
  rate processed by each honest node, and any saturated-network-queue drops;
- the client submits its normal workload only to node0, node2, and node3, so no
  `connection not available` warnings for node1 are expected. Node1 remains in
  the four-node HotStuff validator set but sends no client acknowledgements;
- all four nodes participate in HotStuff, the cluster continues committing
  blocks, and the client produces a final aggregate report;
- compare three repeated normal runs with three repeated attack runs using the
  median ordering latency and similar reported attack rates. The archived
  single-run examples give the following average latencies; each cell is shown
  as `latency (samples)`, and the arrow denotes normal to attack:

  | Protocol | Ordering latency: normal → attack | Consensus latency: normal → attack |
  |---|---:|---:|
  | Pompe | 3.14 ms (1,000) → 19.83 ms (746), **6.3x** | 345.95 ms (996) → 443.42 ms (737), 1.28x |
  | Isotaxis/SMROL | 25.91 ms (341) → 21.67 ms (336), 0.84x | 168.96 ms (341) → 161.37 ms (331), 0.96x |

  The most visible local attack effect is therefore Pompe's ordering latency,
  while Isotaxis/SMROL ordering latency remains comparable to its normal run.
  The source reports are the [Pompe normal](log-examples/attack-logs/pompe/normal/load_test.log),
  [Pompe attack](log-examples/attack-logs/pompe/attack/load_test.log),
  [Isotaxis/SMROL normal](log-examples/attack-logs/smrol/normal/load_test.log),
  and [Isotaxis/SMROL attack](log-examples/attack-logs/smrol/attack/load_test.log)
  client logs. The smaller Pompe consensus increase is a secondary local effect
  of ordering delay and resource contention; node1 participates normally in
  HotStuff, so its leader views do not add a fixed timeout. Because the archived
  attack logs contain fewer completed samples than the normal logs, they support
  a qualitative comparison rather than a claim that all 1,000 submitted
  transactions completed;
- the paper result changes Isotaxis from 2.597 s to 3.067 s and 1155 tx/s to
  978 tx/s, while Pompe changes from 2.030 s to 33.474 s and 1478 tx/s to
  90 tx/s. Exact values are not expected from this four-node smoke test, and the
  archived local values above are illustrative rather than acceptance thresholds.

#### Result location

- client captured latencies: [logs/load_test.log](logs/load_test.log);
- HotStuff throughput: [logs/node/](logs/node/);
- attacker output and a preserved copy of the run:

```bash
cp -R logs ae-results/local-adversary-logs
docker compose -f docker-compose.attack.yml logs --no-color node1 \
  > ae-results/local-pure-attacker.log
```


### Cleanup

```bash
docker compose --profile "*" down
```

## Paper Claims and Experiment Mapping

| Claim | Paper location | Artifact experiment | Validation criterion |
|---|---|---|---|
| **C1: Sparse-load latency scales more favorably.** Latency increases with the number of nodes for both protocols, but Pompe's confirmation latency grows faster than Isotaxis's; at `n=100`, the paper reports roughly 22 s for Pompe and 12 s for Isotaxis. | Fig. 5 and Sec. VIII, *Latency* | E1.1 with `ORDERING_BATCH_SIZE=1`; E2 (`latency.pdf`); (Optional: E3 for full global evaluation) | E1.1 checks the sparse four-node execution path, and E2 must regenerate Fig. 5 with the reported increasing-latency trend and lower Isotaxis latency as `n` grows. |
| **C2: Isotaxis provides a better throughput--latency trade-off as the deployment scales.** Batching initially increases throughput, while very large batches eventually reach resource or network limits; the performance gap between Isotaxis and Pompe grows with `n`. At `n=100` and batch size approximately `1.3 × 10^4`, the paper reports more than 28,000 tx/s for Isotaxis, nearly twice Pompe's throughput. | Figs. 3 and 6 and Sec. VIII, *Throughput* and *Throughput-latency tradeoff* | E1.1 with larger `ORDERING_BATCH_SIZE`; E2 (`tradeoff-100-intro.pdf`, `tps-*.pdf`, and `tradeoff-*.pdf`); (Optional: E3 for full global evaluation) | E1.1 checks the qualitative batching behavior locally. E2 must regenerate Figs. 3 and 6, while E3 validates the throughput--latency curves at the node count selected by `plan-x.json`. |
| **C3: Isotaxis is substantially more robust to ordering-layer DoS flooding than Pompe.** With one Byzantine process continuously flooding sequencing requests, the paper reports Isotaxis changing from 2.597 s to 3.067 s and from 1,155 tx/s to 978 tx/s, while Pompe changes from 2.030 s to 33.474 s and from 1,478 tx/s to 90 tx/s. | Figs. 2 and 7 and Sec. VIII, *Performance robustness under Denial-of-Service (DoS) attack* | E1.2; E2 (`attacks-intro.pdf` and `attacks-exp.pdf`); (Optional: E3 for full global evaluation) | E1.2 must keep committing with the attacker active and reproduce the qualitative normal-versus-attack trend: Isotaxis ordering latency remains comparatively stable, whereas Pompe degrades sharply. E2 must regenerate Figs. 2 and 7 with the paper values. |

Only claims that can be tested using the submitted artifact should appear here.
The paper's safety, liveness, resilience-bound, and asymptotic communication-
complexity claims require proofs and are outside the artifact-evaluation scope.

## E2: Analyze the Archived Paper Results


### E2 execution: regenerate the paper figures

This is the evaluator-facing execution step for E2. It regenerates the paper
figures from the processed numerical data embedded in [gen-fig.py](gen-fig.py). Run the
following commands from the artifact repository root. A virtual environment
avoids modifying the evaluator's system Python installation.

```bash
python3 --version                    # Python 3.9 or newer
python3 -m venv .venv-ae
source .venv-ae/bin/activate         # Windows: .venv-ae\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements-plot.txt
mkdir -p python-fig
python gen-fig.py
```

The script should exit without an exception and write ten PDF files under
[python-fig/](python-fig/): `tps-16.pdf`, `tps-64.pdf`, `tps-100.pdf`,
`tradeoff-16.pdf`, `tradeoff-64.pdf`, `tradeoff-100.pdf`,
`tradeoff-100-intro.pdf`, `latency.pdf`, `attacks-intro.pdf`, and
`attacks-exp.pdf`. The numerical data used by these plots are embedded in
[gen-fig.py](gen-fig.py); this command does not run the distributed experiments. For the
Reproduced badge, the artifact must additionally document how each embedded
series was derived from the archived raw logs and map every generated PDF to
the corresponding paper figure.


## E3: AWS Global Multi-node Evaluation for Figure 6 (~ 5 minuts per run)

E3 is the scale-up global WAN experiment for Figure 6. All node counts use the
same deployment, execution, collection, and cleanup pipeline; they are not
separate scaled and full experiment profiles. The selected
[plan file](ec2/plans/) (`plan-x.json`) determines the deployment size `n` and the regional
distribution. For example, use `plan-16.json`, `plan-64.json`, or
`plan-100.json` for the three node counts plotted in Figure 6, or select another
provided plan when evaluating a different `n`.

The paper deploys each process on an Amazon EC2 `c6a.2xlarge` instance (8 vCPUs
and 16 GB RAM), uses one `t3.micro` instance as the client, and distributes the
processes across 11 global regions to emulate a WAN. Before running E3, record
the selected plan, resulting node count, regions, offered TPS, batch sizes,
duration, repetition count, and estimated cost.

### AWS CLI, SSH key, and container image

E3 requires AWS CLI v2. The scripts use the active AWS profile and do not embed
credentials. Verify the CLI and account before starting any instance:

```bash
aws --version                 # must report aws-cli/2.x
aws sts get-caller-identity   # verify the intended account/profile
```

The repository does not contain or assume an SSH private key. E3 can be run
only when the authors provide access to a prepared evaluation environment, or
when the evaluator deliberately uses their own AWS account and EC2 key pair.
Set the private key authorized for the selected client and replicas before
invoking `make`; the default login is `ubuntu`:

```bash
cd ec2
export SSH_KEY_PATH="$HOME/.ssh/my-ec2-key.pem"
export SSH_USER=ubuntu
chmod 600 "$SSH_KEY_PATH"
```

On macOS, the system Bash is too old for the EC2 scripts. Install a current
Bash and pass it to Make, for example `make BASH_BIN=/opt/homebrew/bin/bash
init`. Linux distributions normally provide a sufficiently recent `bash`.

`SSH_KEY_PATH` is consumed by [ec2/Makefile](ec2/Makefile),
[ec2/init-ec2.sh](ec2/init-ec2.sh), and
[ec2/deploy-ec2.sh](ec2/deploy-ec2.sh); these commands stop with an error when
the variable is absent or unreadable. The selected EC2 instances must already
accept the corresponding public key. Never commit or place a private key in the
artifact repository. If the evaluator needs to import their own public key into
the regions listed in `ec2/regions.txt`, configure the separate variables used
by [ec2/upload_pubkey.sh](ec2/upload_pubkey.sh):

```bash
EC2_KEY_NAME=my-ec2-key \
SSH_PUBLIC_KEY_PATH="$HOME/.ssh/my-ec2-key.pub" \
./ec2/upload_pubkey.sh
```

The EC2 Compose files pull the public linux/amd64 image directly
from Docker Hub. The default is pinned to the evaluated immutable digest:

```text
georgiaxr/hs-test:latest@sha256:143eaa72aec71dbc287176ff05f9e65207e5027d7a6abd76b970d06684541e31
```

Set `HOTSTUFF_IMAGE` only when intentionally evaluating another author-provided
image. `make pull` downloads the configured image on every selected host.

### AWS security-group prerequisites

Create and attach an appropriate security group in every selected region before
running E3. The rules below follow the configuration used for the paper, but
their sources must be adapted to the evaluator's account and experiment
instances.

| Direction | Protocol and ports | Allowed source/destination | Purpose |
|---|---|---|---|
| Inbound | TCP 22 | Evaluator's public IP `/32` only | SSH and SCP |
| Inbound | TCP 9000--22000 | Public `/32` addresses or a controlled CIDR containing only the participating client and replica instances | Client, HotStuff, Pompe, and Isotaxis communication |
| Outbound | All traffic | `0.0.0.0/0` | Package installation and Docker image access |

Security-group IDs, AWS account IDs, and fixed IP addresses from an author's
environment are not portable and must not be reused unchanged. In particular,
do not expose SSH to `0.0.0.0/0`. The provided
[ec2/copy_security_group.sh](ec2/copy_security_group.sh) clones a source group
chosen through `SOURCE_SECURITY_GROUP_ID`; it does not contain an author
account or group ID. When
`NODE_IP_SOURCE=public` is used across regions, allow the public `/32` address
of every participating instance in the TCP 9000--22000 rule.

Before any live operation, inspect a plan using dry-run mode:

```bash
cd ec2
NODE_INSTANCE_TYPE=c6a.2xlarge \
  ./start_instances.sh --plan plans/plan-16.json --dry-run
```

Replace `16` with the desired `n`. The corresponding `plan-x.json` controls
which stopped instances are selected in each region.

Do not remove `--dry-run` unless the evaluator has reviewed the plan, confirmed
the estimated cost, backed up existing logs, and received author-provided
credentials or explicit authorization to use their own account.

The current live workflow starts pre-existing instances, discovers their
addresses, generates configuration, deploys containers, runs the experiment,
collects selected logs, and stops the containers. Each step is explicit;
`get_ips.sh`, `make init`, `make deploy`, and `make pull` do not start the
experiment:

```bash
# COSTLY AND STATE-CHANGING; shown for documentation only.
cd ec2
./start_instances.sh --plan plans/plan-16.json
NODE_IP_SOURCE=public ./get_ips.sh
make init       # Install Docker Engine and the Docker Compose v2 plugin
make deploy     # Upload generated environment and Compose files
make pull       # Pull the pinned Docker Hub image; no source build or push
make start      # Run for two minutes, stop containers, and collect logs

# First inspect which running instances would be stopped. Then supply exactly
# the Name tags of the instances started for this experiment.
./stop_instances.sh --dry-run
INSTANCE_NAMES=client,my-replica-1,my-replica-2
./stop_instances.sh --names "$INSTANCE_NAMES"
or
./stop_instances.sh # stops all running instances
```

Raw logs are collected under the generated `ec2/ec2-logs/` directory. Copy them into a unique,
non-overwritten result directory before starting another configuration.

| Paper result | Plan and node count | Protocol/mode | Workload | Expected output |
|---|---|---|---|---|
| Figure 6 | Select `plans/plan-x.json`; the selected `x` determines `n` (`16`, `64`, and `100` correspond to the paper plots) | Isotaxis-HS and Pompe-HS | Sweep the documented offered TPS and batch sizes for the selected `n` (the paper evaluates batches up to `1.6 × 10^5` transactions) | Client latency logs and per-node committed-throughput logs under `ec2/ec2-logs/`, sufficient to reconstruct the corresponding Figure 6 curves |

Evaluators may choose any provided plan according to their AWS budget and
available time. A smaller `n` is a shorter execution of the same E3 workflow,
not a different experiment. Clearly record the chosen plan and do not present a
run at one `n` as an exact reproduction of a different Figure 6 node count.

## Configuration and Customization

The normal local configuration is stored in [.env](.env), while the attack-only
configuration is stored in [.attack.env](.attack.env).
Other important settings include:

| Variable | Meaning |
|---|---|
| `NODE_NUM` | Number of replicas in the local deployment |
| `NODE_HOSTS` | Replica-name/address mapping |
| `CLIENT_EXCLUDED_NODE_IDS` | Comma-separated identities excluded only from client workload submission; attack mode uses `1` |
| `CLIENT_ORDERING_MODE` | Ordering protocol selected by the client; `smrol` selects SMR-OL |
| `TARGET_TPS` | Offered workload rate; deprecated |
| `POMPE_ENABLE` | Enables the ordering-to-HotStuff integration path |
| `POMPE_BATCH_SIZE` | Ordering batch size |
| `POMPE_ATTACK_WORKERS` | Concurrent Pompe flooding tasks inside node1 |
| `ATTACK_REPORT_INTERVAL_SECS` | Interval for compact attacker rate reports |
| `POMPE_STABLE_PERIOD_MS` | Stable-period parameter |
| `POMPE_LIVENESS_DELTA_MS` | Liveness timeout parameter |
| `HS_MAX_VIEW_TIME_MS` | HotStuff maximum view time |
| `SMROL_DISABLE_MULTISIG` | Set to `0` to exercise multisignatures |
| `SMROL_DISABLE_METRICS` | Set to `0` to expose runtime metrics |
| `SMROL_*_WORKERS` | Worker counts for threshold, sequencing, and signature work |
| `SMROL_*_CORES` | CPU-affinity sets for the corresponding workers |

To preserve comparability, copy the complete configuration used by each paper
experiment into a versioned file rather than asking evaluators to edit [.env](.env)
manually. Record the evaluated commit and container digest alongside every raw
result directory.

## Output and Result Interpretation

The client writes workload logs under the shared [logs/](logs/) volume and reports:

- ordering latency;
- end-to-end consensus latency;
- P50 and other latency quantiles;
- sent, confirmed, and failed transaction counts;
- observed client TPS and success rate.

Replicas report:

- committed block height and transaction count;
- end-to-end, pure-consensus, and submission TPS;
- total committed transactions and blocks;
- optional SMR-OL runtime metrics.

Performance results are affected by CPU model, CPU affinity, Docker overhead,
network topology, cloud placement, and transient WAN conditions. For every
non-deterministic result, the final version of this guide must state an expected
range or tolerance and the number of repetitions used in the paper.

## Troubleshooting

### Docker Compose v2 is not available

All evaluator-facing commands and helper scripts use Compose v2
(`docker compose`). Install the Docker Compose plugin if `docker compose
version` fails; the legacy standalone `docker-compose` command is not required.

### No latency summaries are visible

Start Compose with `LOG_LEVEL=info`, wait until transactions have committed, and
inspect the `load_tester` log and the files under [logs/](logs/).

### CPU affinity fails

Adjust or remove the `*_CORES` values in [.env](.env). Document any change when
reporting performance because it may affect the paper comparison.

### Plot input is missing

Confirm that the artifact-data archive was downloaded and extracted at the path
documented by E2. The development repository alone does not currently contain
the inputs expected by [gen-fig.py](gen-fig.py).

## Licenses and Third-Party Material

The authors' original code in this artifact is licensed under the
[Apache License 2.0](LICENSE). Third-party components retain their original
licenses and copyright notices. This includes the bundled `hotstuff_rs` source,
Pompe-HS, Salticidae, bundled papers, raw logs, and any other redistributed
third-party material. The bundled HotStuff code is derived from
`parallelchain-io/hotstuff_rs` version 0.4.0, is distributed under Apache-2.0,
and contains artifact-specific changes required by the runner and attack
experiments. The DOI archive must contain only material that may legally be
redistributed.
