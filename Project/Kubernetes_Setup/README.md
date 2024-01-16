# Kubernetes Setup

## Structure

This Kubernetes setup is divided into 5 relevant namespaces

- arkouda
- forgejo
- pachyderm
- registry


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

