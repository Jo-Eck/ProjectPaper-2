#!/bin/bash

# Define color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Initialize error flag
error_flag=0

# Function to print info messages
info() {
    echo -e "${GREEN}[INFO] $1${NC}"
}

# Function to print error messages
fail() {
    echo -e "${RED}[ERROR] $1${NC}"
    error_flag=1
}

# Checking installation of necessary packages
dpkg -l | grep -qw apt-transport-https || fail "apt-transport-https is not installed"
dpkg -l | grep -qw ca-certificates || fail "ca-certificates is not installed"
dpkg -l | grep -qw curl || fail "curl is not installed"
dpkg -l | grep -qw kubelet || fail "kubelet is not installed"
dpkg -l | grep -qw kubeadm || fail "kubeadm is not installed"
dpkg -l | grep -qw kubectl || fail "kubectl is not installed"
dpkg -l | grep -qw containerd || fail "containerd is not installed"

# Check Kubernetes APT source list
grep -q "https://apt.kubernetes.io/ kubernetes-xenial main" /etc/apt/sources.list.d/kubernetes.list || fail "Kubernetes APT source list is not configured correctly"

# Check if swap is disabled
swapon --summary | grep -q swap && fail "Swap is not disabled"

# Check containerd configuration
grep -q 'SystemdCgroup = true' /etc/containerd/config.toml || fail "SystemdCgroup is not enabled in containerd configuration"

# Check sysctl parameters
[ "$(cat /proc/sys/net/bridge/bridge-nf-call-iptables)" == "1" ] || fail "bridge-nf-call-iptables is not enabled"
[ "$(cat /proc/sys/net/ipv4/ip_forward)" == "1" ] || fail "ip_forward is not enabled"

# Check proxy settings for services
[ -f /etc/systemd/system/containerd.service.d/http-proxy.conf ] || fail "Proxy settings for containerd service is not configured"
[ -f /etc/systemd/system/kubelet.service.d/http-proxy.conf ] || fail "Proxy settings for kubelet service is not configured"

# Check Kubernetes node status
if command -v kubectl &> /dev/null; then
    kubectl get nodes || fail "Failed to get Kubernetes nodes. Check if the node has joined the cluster successfully"
else
    info "kubectl command not found. Skipping Kubernetes node check"
fi

# Check status of services
if systemctl --all --type=service --state=active | grep -qw containerd; then
    systemctl is-active --quiet containerd || fail "containerd service is not running"
else
    info "containerd service not found. Skipping service status check"
fi

if systemctl --all --type=service --state=active | grep -qw kubelet; then
    systemctl is-active --quiet kubelet || fail "kubelet service is not running"
else
    info "kubelet service not found. Skipping service status check"
fi

# Print summary
if [ $error_flag -eq 0 ]; then
    info "All checks passed successfully."
else
    echo -e "${RED}Some checks failed. Please check the error messages above.${NC}"
fi
