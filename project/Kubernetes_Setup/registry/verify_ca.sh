#!/bin/bash

# Path to the certificate on the remote nodes
REMOTE_CERTIFICATE_PATH="./ca.crt"

# Path to the SSH key
SSH_KEY_PATH="/home/jon/.ssh/work/second_key"

# Path to the file containing the list of nodes (one per line)
NODES_FILE="nodes.txt"

# Username with sudo su access
REMOTE_USER="eckerth"

# ANSI escape codes for colors
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Loop through each node and execute the checks
while IFS= read -r node
do
  echo -e "Verifying ${GREEN}$node${NC} ..."

  # Check if the certificate file exists
  ssh -i "$SSH_KEY_PATH" -o LogLevel=ERROR "$REMOTE_USER@$node" > /dev/null 2>&1 <<EOF
    sudo su - <<'END_ROOT'
      if [ -f "$REMOTE_CERTIFICATE_PATH" ]; then
        echo -e "${GREEN}Certificate found on $node${NC}"
      else
        echo -e "${RED}Certificate NOT found on $node${NC}"
      fi

      # Check if the containerd service is active
      if systemctl is-active --quiet containerd; then
        echo -e "${GREEN}containerd is running on $node${NC}"
      else
        echo -e "${RED}containerd is NOT running on $node${NC}"
      fi
    END_ROOT
EOF

  echo "Verification completed for $node"
done < "$NODES_FILE"

echo "Verification process complete for all nodes."
