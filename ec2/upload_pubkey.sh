#!/usr/bin/env bash
set -euo pipefail

EC2_KEY_NAME="${EC2_KEY_NAME:-}"
SSH_PUBLIC_KEY_PATH="${SSH_PUBLIC_KEY_PATH:-}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REGIONS_FILE="$SCRIPT_DIR/regions.txt"

if [[ -z "$EC2_KEY_NAME" || -z "$SSH_PUBLIC_KEY_PATH" ]]; then
  echo "EC2_KEY_NAME and SSH_PUBLIC_KEY_PATH are required." >&2
  exit 1
fi

if [[ ! -f "$SSH_PUBLIC_KEY_PATH" ]]; then
  echo "Public key not found: $SSH_PUBLIC_KEY_PATH" >&2
  exit 1
fi

if [[ ! -f "$REGIONS_FILE" ]]; then
  echo "Regions file not found: $REGIONS_FILE" >&2
  exit 1
fi

mapfile -t REGIONS < <(sed -e 's/#.*//' -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' "$REGIONS_FILE" | awk 'NF > 0')

if (( ${#REGIONS[@]} == 0 )); then
  echo "Regions list is empty (check $REGIONS_FILE)" >&2
  exit 1
fi

for region in "${REGIONS[@]}"; do
  echo "→ Uploading $EC2_KEY_NAME to $region"
  if aws ec2 import-key-pair \
      --region "$region" \
      --key-name "$EC2_KEY_NAME" \
      --public-key-material "fileb://$SSH_PUBLIC_KEY_PATH" >/dev/null; then
    echo "   $region: key imported"
  else
    echo "   $region: import failed (maybe it already exists)" >&2
  fi
done
