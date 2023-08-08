#!/bin/bash

# Path to the certificate on your local machine
CERTIFICATE_PATH="./ca.crt"

# Path to the SSH key
SSH_KEY_PATH="/home/jon/.ssh/work/second_key"

# Path to the file containing the list of nodes (one per line)
NODES_FILE="nodes.txt"

# Username with sudo su access
REMOTE_USER="eckerth"

# Loop through each node and execute the commands
while IFS= read -r node
do
  echo "Processing $node ..."

  # Copy the certificate to the node's home directory (or another temporary location)
  scp -i "$SSH_KEY_PATH" "$CERTIFICATE_PATH" "$REMOTE_USER@$node:/tmp/ca.crt" > /dev/null 2>&1

  # Execute the commands as the remote user, using sudo su to switch to root
  ssh -i "$SSH_KEY_PATH" -o LogLevel=ERROR "$REMOTE_USER@$node" > /dev/null 2>&1 <<EOF
    sudo su - <<'END_ROOT'
      mv /tmp/ca.crt /usr/local/share/ca-certificates/ca.crt
      update-ca-certificates
      systemctl restart containerd # <-- Replace this with the correct command if needed
    END_ROOT
EOF

  echo "Completed $node"
done < "$NODES_FILE"

echo "Done processing all nodes."
