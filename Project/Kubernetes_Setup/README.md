# Kubernetes Setup

## Structure

This Kubernetes setup is divided into 5 relevant namespaces

- arkouda
- forgejo
- pachyderm
- registry

## Setting up kubernetes on the heydar cluster

This is a documentation of the steps I took to install kubernetes on the heydar machines

### Proxies

As always we need to set up the proxies. This is done by running the following command:

```bash
export https_proxy=http://proxy.its.hpecorp.net:80
export HTTPS_PROXY=${https_proxy}
export HTTP_PROXY=${https_proxy}
export http_proxy=${https_proxy}
export no_proxy=localhost,127.0.0.1,10.0.0.0/8,172.16.0.0/16,10.93.246.68/28
export NO_PROXY=${no_proxy}
```

### Setting up master node

#### Instaling packages

Now we install the packages and add the repos we need:

```bash
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl
curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-archive-keyring.gpg
echo "deb [signed-by=/etc/apt/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo apt-get update
sudo apt-get install -y kubelet kubeadm kubectl containerd
sudo apt-mark hold kubelet kubeadm kubectl 
```

#### Setting up containerd

Now we need to set up containerd. We do this by creating a default config file for containerd:

```bash
sudo mkdir -p /etc/containerd
sudo containerd config default | sudo tee /etc/containerd/config.toml
```

we then have to enable systemd cgroup driver.
This is done by switching the `SystemdCgroup` variable under  `[plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc.options]` to `true`:

This can quickly be done by running the following command:

```bash
sudo sed -i 's/            SystemdCgroup = false/            SystemdCgroup = true/' /etc/containerd/config.toml
```

#### Enabling br_netfilter and ipforwarding

We need to enable br_netfilter so that the nodes can communicate with each other:

```bash
modprobe br_netfilter
echo '1' > /proc/sys/net/bridge/bridge-nf-call-iptables
```

We also need to enable ip forwarding so that the nodes can communicate with the outside world:

```bash
echo '1' > /proc/sys/net/ipv4/ip_forward
```

And to make them persistent we need to add the following lines to `/etc/sysctl.conf`:

```bash
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.ip_forward = 1
```

And then run the following command to apply the changes:

```bash
sysctl -p
```

#### Disabling swap

Kubernetes does not work with swap enabled so we need to permanently disable it:

```bash
sudo swapoff -a
sudo sed -i -e '/ swap / s/^/#/' -e '/\/swap.img/ s/^/#/' /etc/fstab # comments out swap in fstab
```

#### Initializing the cluster

Now we initialize the cluster. Fist we switch to root user:

```bash
sudo su
```

Now we have to choose the pod network cidr. This is the range of ip addresses that will be used by the pods.
In my case im choosing the pod network cidr to be `172.16.0.0/16` because the local network already uses `10.x.x.x` and I want easily distinguishable ip addresses.

As for the apiserver-advertise-address, this is the ip address that the master node will use to advertise itself to the other nodes.
I want to use haydar20 as the master node so I will use its ip address `10.93.246.87` as the apiserver-advertise-address.

```bash
kubeadm init --pod-network-cidr=172.16.0.0/16 --apiserver-advertise-address=10.93.246.87
```

Now you should see something along the lines of:

```bash

Your Kubernetes control-plane has initialized successfully!

To start using your cluster, you need to run the following as a regular user:

  mkdir -p $HOME/.kube
  sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
  sudo chown $(id -u):$(id -g) $HOME/.kube/config

Alternatively, if you are the root user, you can run:

  export KUBECONFIG=/etc/kubernetes/admin.conf

You should now deploy a pod network to the cluster.
Run "kubectl apply -f [podnetwork].yaml" with one of the options listed at:
  https://kubernetes.io/docs/concepts/cluster-administration/addons/

Then you can join any number of worker nodes by running the following on each as root:

sudo kubeadm join 10.93.246.87:6443 --token ske9kq.rgg1juirtyinx924 \
--discovery-token-ca-cert-hash sha256:52f8e86c7f96728af0ea9c8c9da3d6cc6d86f31a48b6239df57331142e9d99b4 
```

Now we need to set up the kubectl config file. This is done by running the following commands:

```bash
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config 
```

#### Setting up the pod network

Now we need to set up the pod network. I will be using calico as the pod network.
This is done by running the following command:

```bash
kubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml
```

### Setting up worker nodes

To delpoy the worker nodes we would need to run the following command on each worker node:

```bash
#!/bin/bash

# Set up the environment variables
export https_proxy=http://proxy.its.hpecorp.net:80
export HTTPS_PROXY=${https_proxy}
export HTTP_PROXY=${https_proxy}
export http_proxy=${https_proxy}
export no_proxy=localhost,127.0.0.1,10.0.0.0/8,172.16.0.0/16,10.93.246.68/28
export NO_PROXY=${no_proxy}

# Installing necessary packages
sudo apt-get update -y
sudo apt-get install -y apt-transport-https ca-certificates curl
curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo gpg --yes --dearmor -o /etc/apt/keyrings/kubernetes-archive-keyring.gpg
echo "deb [signed-by=/etc/apt/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo apt-get update -y
sudo apt-get install -y kubelet kubeadm kubectl containerd
sudo apt-mark hold kubelet kubeadm kubectl 

# Enable modules and sysctl parameters
sudo modprobe br_netfilter
echo '1' | sudo tee /proc/sys/net/bridge/bridge-nf-call-iptables
echo '1' | sudo tee /proc/sys/net/ipv4/ip_forward
sudo sysctl -p

# Disable swap
sudo swapoff -a
sudo sed -i -e '/ swap / s/^/#/' -e '/\/swap.img/ s/^/#/' /etc/fstab # comments out swap in fstab

# Join the Kubernetes cluster
sudo kubeadm join 10.93.246.87:6443 --token ske9kq.rgg1juirtyinx924 \
--discovery-token-ca-cert-hash sha256:52f8e86c7f96728af0ea9c8c9da3d6cc6d86f31a48b6239df57331142e9d99b4 ```

But to make my live easier I decided to use ansible to deploy the worker nodes.

### Setting up ansible

First we need to install ansible on the master node:

```bash
sudo apt-get update -y
sudo apt-get install -y ansible
```

Now we need to set up the ansible hosts file.
This is done by adding the following lines to `/etc/ansible/hosts`:

```bash
[heydar_nodes]
10.93.246.68  ansible_host=Heydar01
10.93.246.69  ansible_host=Heydar02
10.93.246.70  ansible_host=Heydar03
10.93.246.71  ansible_host=Heydar04
10.93.246.72  ansible_host=Heydar05
10.93.246.73  ansible_host=Heydar06
10.93.246.74  ansible_host=Heydar07
10.93.246.75  ansible_host=Heydar08
10.93.246.76  ansible_host=Heydar09
10.93.246.77  ansible_host=Heydar10
10.93.246.78  ansible_host=Heydar11
10.93.246.79  ansible_host=Heydar12
10.93.246.80  ansible_host=Heydar13
10.93.246.81  ansible_host=Heydar14
10.93.246.82  ansible_host=Heydar15
10.93.246.83  ansible_host=Heydar16
10.93.246.84  ansible_host=Heydar17
10.93.246.85  ansible_host=Heydar18
10.93.246.86  ansible_host=Heydar19
10.93.246.87  ansible_host=Heydar20
```

Then we create a new ansible playbook called `join_cluster.yml`:

```bash
---
- hosts: heydar_nodes
  become: yes
  tasks:
    - name: Setting up environment variables
      lineinfile:
        path: /etc/environment
        line: "{{ item }}"
      with_items:
        - "https_proxy=http://proxy.its.hpecorp.net:80"
        - "HTTP_PROXY=http://proxy.its.hpecorp.net:80"
        - "http_proxy=http://proxy.its.hpecorp.net:80"
        - "NO_PROXY=localhost,127.0.0.1,10.0.0.0/8,172.16.0.0/16,10.93.246.68/28"

    - name: Update and install necessary packages
      apt:
        name: "{{ packages }}"
        update_cache: yes
      vars:
        packages:
          - apt-transport-https
          - ca-certificates
          - curl

    - name: Add Kubernetes apt-key
      shell: |
        curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --yes --dearmor -o /etc/apt/keyrings/kubernetes-archive-keyring.gpg
        echo "deb [signed-by=/etc/apt/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | tee /etc/apt/sources.list.d/kubernetes.list
        apt-get update -y
        apt-get install -y kubelet kubeadm kubectl containerd
        apt-mark hold kubelet kubeadm kubectl

    - name: Enable necessary kernel modules and sysctl parameters
      shell: |
        modprobe br_netfilter
        echo '1' > /proc/sys/net/bridge/bridge-nf-call-iptables
        echo '1' > /proc/sys/net/ipv4/ip_forward
        sysctl -p

    - name: Disable swap
      shell: |
        swapoff -a
        sed -i -e '/ swap / s/^/#/' -e '/\/swap.img/ s/^/#/' /etc/fstab # comments out swap in fstab

    - name: Join the Kubernetes cluster
      shell: |
        kubeadm join 10.93.246.87:6443 --token 0v7aoq.65ib2v0g70a6em49 --discovery-token-ca-cert-hash sha256:9cb5e62dd86cd7e94718c866575cd023c98cc89f2849dad3d25dfd75b13d1b72
```

Now we can run the playbook by running the following command:

```bash
ansible-playbook -i /etc/ansible/hosts join_cluster.yml
```



## Setting up the GitOps CI/CD

This part is concerned with setting up both the Version Control System Forgejo and the CI/CD system Jenkins. \
While Forgeo is a fork of Gitea, it is still sparcely documented and thus we will not setup the runner system of Forgejo, but instead use Jenkins for CI/CD.


### Namespaces

As always we create namespaces to keep things clean:

```bash
kubectl create namespace forgejo
kubectl create namespace jenkins
```

### Persistent Volumes

We need to create a location for the persistent volume:

```bash
mkdir -p /mnt/forgejo/postgres
mkdir -p /mnt/forgejo/zero
mkdir -p /mnt/jenkins
sudo chown -R eckerth:users /mnt/forgejo/  /mnt/jenkins
```

We then create the persistent volumes for Forgejo ....:

``` yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: forgejo
provisioner: kubernetes.io/no-provisioner
volumeBindingMode: WaitForFirstConsumer
---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: forgejo-postgres
  labels:
    type: local
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteOnce
  storageClassName: forgejo
  local:
    path: /mnt/forgejo/postgres
  nodeAffinity:
    required:
      nodeSelectorTerms:
      - matchExpressions:
        - key: kubernetes.io/hostname
          operator: In
          values:
          - heydar20.labs.hpecorp.net
---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: forgejo-0
  labels:
    type: local
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteOnce
  storageClassName: forgejo
  local:
    path: /mnt/forgejo/zero
  nodeAffinity:
    required:
      nodeSelectorTerms:
      - matchExpressions:
        - key: kubernetes.io/hostname
          operator: In
          values:
          - heydar20.labs.hpecorp.net

```

... and for Jenkins:

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: jenkins
provisioner: kubernetes.io/no-provisioner
volumeBindingMode: WaitForFirstConsumer

---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: jenkins
  labels:
    type: local
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteOnce
  storageClassName: jenkins
  local:
    path: /mnt/jenkins
  nodeAffinity:
    required:
      nodeSelectorTerms:
      - matchExpressions:
        - key: kubernetes.io/hostname
          operator: In
          values:
          - heydar20.labs.hpecorp.net
```

```bash
kubectl -n  forgejo apply -f ./forgejo/volumes.yaml
kubectl -n  jenkins apply -f ./jenkins/volumes.yaml
```

### Installation

After these are applied we can simply install the helm chart:

```bash
helm repo add jenkins https://charts.jenkins.io
helm repo update
helm install -n jenkins jenkins jenkins/jenkins -f ./jenkins/values.yaml
helm install -n forgejo forgejo oci://codeberg.org/forgejo-contrib/forgejo -f ./forgejo/values.yaml 
```

### Configuring

In order to connect both Jenkins and Forgeo we will have to adjust some configurations.

1. As we want Jenkins to be able to be able spawn pods on the cluster, we will need to give it the needed permissions.
For this one can use the service_account.yaml file in the jenkins folder.

```bash
kubectl -n jenkins apply -f ./jenkins/service_account.yaml
```

2. We add the following config map to Forgejo in order to allow it to send webhooks to out jenkins host.

```yaml
additionalConfigSources:
      - configMap:
         name: gitea-app-ini
```

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: gitea-app-ini
data:
  webhook: |
   ALLOWED_HOST_LIST=<jenkins server>
```

```bash
kubectl -n forgejo apply -f ./forgejo/configmap.yaml
```

2. We then have to go into the Forgejo admin pannel and enable the system wide Webhooks,

