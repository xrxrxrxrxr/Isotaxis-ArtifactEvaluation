#!/usr/bin/env bash
# deploy-ec2.sh

set -euo pipefail

if [[ -z "${SSH_KEY_PATH:-}" ]]; then
  echo "SSH_KEY_PATH is required; set it to the private key for the selected EC2 instances." >&2
  exit 1
fi
if [[ ! -r "$SSH_KEY_PATH" ]]; then
  echo "SSH private key is not readable: $SSH_KEY_PATH" >&2
  exit 1
fi
SSH_USER="${SSH_USER:-ubuntu}"
SSH_OPTS="-i $SSH_KEY_PATH -o StrictHostKeyChecking=accept-new -o BatchMode=yes -o LogLevel=ERROR"

# Read hosts.txt
declare -A PUBLIC_IPS PRIVATE_IPS
declare -a NODE_NAMES

echo "Reading hosts.txt..."
while IFS=' ' read -r ip name; do
  # Skip comments and empty lines
  [[ $ip =~ ^#.*$ || -z $ip ]] && continue
  
  if [[ ! $name =~ -private$ ]]; then
    PUBLIC_IPS[$name]=$ip
    echo "  ✓ $name = $ip"
    if [[ $name =~ ^node[0-9]+$ ]]; then
      NODE_NAMES+=("$name")
    fi
  else
    base_name=${name%-private}
    PRIVATE_IPS[$base_name]=$ip
  fi
done < hosts.txt

echo ""

# Verify we loaded the IP list
if [[ ${#PUBLIC_IPS[@]} -eq 0 ]]; then
  echo "Error: failed to read any IP from hosts.txt"
  echo "Please check the format of hosts.txt"
  exit 1
fi

# Sort discovered node names numerically (node0, node1, ...)
if [[ ${#NODE_NAMES[@]} -gt 0 ]]; then
  IFS=$'\n' NODE_NAMES=($(printf '%s\n' "${NODE_NAMES[@]}" | sort -V))
  unset IFS
fi

if [[ ${#NODE_NAMES[@]} -eq 0 ]]; then
  echo "Error: no node entries found in hosts.txt"
  exit 1
fi

echo "Starting deployment to EC2..."
echo ""

# Deploy all nodes discovered in hosts.txt (in parallel)
declare -a DEPLOY_PIDS
STATUS=0

for name in "${NODE_NAMES[@]}"; do
  (
    ip="${PUBLIC_IPS[$name]}"
    if [[ -z "$ip" ]]; then
      echo "Error: IP for $name not found"
      exit 1
    fi

    # 给这个节点的所有输出加前缀（防止并发输出交错导致误判）
    exec > >(sed -u "s/^/[$name $ip] /") 2>&1

    echo "Deploying $name ($ip)..."

    set -e
    REMOTE_BASE="/home/$SSH_USER/hotstuff"

    ssh $SSH_OPTS "$SSH_USER@$ip" "sudo mkdir -p $REMOTE_BASE/logs && sudo chown -R $SSH_USER:$SSH_USER $REMOTE_BASE"
    ssh $SSH_OPTS "$SSH_USER@$ip" "mkdir -p $REMOTE_BASE/logs"
    scp $SSH_OPTS docker-compose-node.yml "$SSH_USER@$ip:$REMOTE_BASE/docker-compose.yml"

    env_file="envs/${name}.env"
    if [[ ! -f "$env_file" ]]; then
      echo "Error: $env_file not found"
      exit 1
    fi

    scp $SSH_OPTS "$env_file" "$SSH_USER@$ip:$REMOTE_BASE/.env"

    echo "$name deployment completed"
    echo ""
  ) &
  DEPLOY_PIDS+=("$!")
done

for pid in "${DEPLOY_PIDS[@]}"; do
  if ! wait "$pid"; then
    echo "Error during node deployment"
    STATUS=1
  fi
done

if [[ $STATUS -ne 0 ]]; then
  echo "Some nodes failed to deploy, aborting"
  exit 1
fi

# Deploy the client
client_ip="${PUBLIC_IPS[client]}"
if [[ -z "$client_ip" ]]; then
  echo "Error: client IP not found"
  exit 1
fi

echo "Deploying client ($client_ip)..."
ssh $SSH_OPTS "$SSH_USER@$client_ip" "mkdir -p ~/hotstuff/logs"
scp $SSH_OPTS docker-compose-client.yml "$SSH_USER@$client_ip:~/hotstuff/docker-compose.yml"
scp $SSH_OPTS envs/client.env "$SSH_USER@$client_ip:~/hotstuff/.env"

echo ""
echo "All files deployed successfully!"
