#!/bin/bash

PROXY="http://web-proxy.labs.hpecorp.net:8080"  # replace with your proxy server and port
NOPROXY="localhost,cluster.local,.cluster.local,.labs.hpecorp.net,127.0.0.1,192.168.0.0/16,10.0.0.0/8,172.16.0.0/12,10.244.0.0/16,10.96.0.0/12,10.93.0.0/16,10.152.0.0/16"

# Function to print info messages
info() {
    echo "[INFO] $1"
}


info "Setting up proxy..."
export http_proxy=$PROXY
export HTTP_PROXY=$PROXY
export https_proxy=$PROXY
export HTTPS_PROXY=$PROXY
export no_proxy="$NOPROXY"
export NO_PROXY="$NOPROXY"

info "Installing necessary packages..."

(
  set -e
  sudo apt-get update -y
  sudo apt-get install -y apt-transport-https ca-certificates curl
  curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo gpg --yes --dearmor -o /etc/apt/keyrings/kubernetes-archive-keyring.gpg
  echo "deb [signed-by=/etc/apt/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list
  sudo apt-get update -y
  sudo apt-get install -y kubelet kubeadm kubectl containerd
  sudo apt-mark hold kubelet kubeadm kubectl 
) || {
  echo "There was an error installing the packages, but the script will continue."
}

info "Configuring containerd..."
sudo mkdir -p /etc/containerd
sudo containerd config default | sudo tee /etc/containerd/config.toml
sudo sed -i 's/            SystemdCgroup = false/            SystemdCgroup = true/' /etc/containerd/config.toml

info "Enabling necessary modules and sysctl parameters..."
sudo modprobe br_netfilter
echo '1' | sudo tee /proc/sys/net/bridge/bridge-nf-call-iptables
echo '1' | sudo tee /proc/sys/net/ipv4/ip_forward
sudo sysctl -p

info "Disabling swap..."
sudo swapoff -a
sudo sed -i -e '/ swap / s/^/#/' -e '/\/swap.img/ s/^/#/' /etc/fstab # comments out swap in fstab

info "Setting up proxy for apt..."
echo "Acquire::http::Proxy \"$PROXY\";" | sudo tee /etc/apt/apt.conf.d/30proxy

info "Setting up proxy for environment variables..."
echo -e "http_proxy=$PROXY\nHTTP_PROXY=$PROXY\nhttps_proxy=$PROXY\nHTTPS_PROXY=$PROXY\nno_proxy=\"$NOPROXY\"\nNO_PROXY=\"$NOPROXY\"" | sudo tee /etc/environment
source /etc/environment

info "Setting up proxy for containerd service..."
sudo mkdir -p /etc/systemd/system/containerd.service.d
cat <<EOF | sudo tee /etc/systemd/system/containerd.service.d/http-proxy.conf
[Service]
Environment="HTTP_PROXY=$PROXY"
Environment="HTTPS_PROXY=$PROXY"
Environment="NO_PROXY=$NOPROXY"
EOF

info "Setting up proxy for kubelet service..."
sudo mkdir -p /etc/systemd/system/kubelet.service.d
cat <<EOF | sudo tee /etc/systemd/system/kubelet.service.d/http-proxy.conf
[Service]
Environment="HTTP_PROXY=$PROXY"
Environment="HTTPS_PROXY=$PROXY"
Environment="NO_PROXY=$NOPROXY"
EOF

info "Reloading the systemd daemon..."
sudo systemctl daemon-reload

info "Restarting containerd and kubelet services..."
sudo systemctl restart containerd
sudo systemctl restart kubelet

info "Proxy configuration completed."
