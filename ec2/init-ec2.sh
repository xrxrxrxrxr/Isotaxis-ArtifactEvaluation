#!/bin/bash
# init-ec2.sh - Install Docker and Docker Compose

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
SSH_OPTS="-i $SSH_KEY_PATH -o StrictHostKeyChecking=accept-new -o BatchMode=yes"

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
HOSTS_FILE="$SCRIPT_DIR/hosts.txt"

if [[ ! -f "$HOSTS_FILE" ]]; then
  echo "hosts.txt not found at $HOSTS_FILE" >&2
  exit 1
fi

mapfile -t TARGETS < <(awk -v user="$SSH_USER" '/(node[0-9]+$|client$)/ {print user"@"$1}' "$HOSTS_FILE")

if [[ ${#TARGETS[@]} -eq 0 ]]; then
  echo "No node/client entries found in hosts.txt" >&2
  exit 1
fi

echo "Initializing EC2 instances (installing Docker)..."

for host in "${TARGETS[@]}"; do
  echo "Initializing $host..."
  ssh $SSH_OPTS $host "
    set -e
    # Update the system
    sudo apt-get update -y

    # Install Docker
    sudo apt-get install -y docker.io

    # Start Docker
    sudo systemctl start docker
    sudo systemctl enable docker

    # Add the current user to the docker group
    sudo usermod -aG docker $SSH_USER

    # Remove legacy docker-compose (if present)
    sudo rm -f /usr/local/bin/docker-compose

    # Install dependencies
    sudo apt-get install -y ca-certificates curl gnupg lsb-release

    # Add the official Docker GPG key
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

    # Add the official Docker apt repository
    echo \"deb [arch=\$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \$(lsb_release -cs) stable\" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    # Update apt and install the docker compose plugin
    sudo apt-get update -y
    sudo apt-get install -y docker-compose-plugin

    # Verify the installation
    docker --version
    docker compose version
  " &
done

wait
echo ""
echo "All instances initialized!"
echo "Note: log in again to refresh docker group permissions"
echo ""
echo "Next steps:"
echo "  make deploy   # Deploy configuration files"
echo "  make start    # Start the experiment"
