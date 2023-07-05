# Pachyderm

## Installation

These instructions are based upon the excellent guide by [Pachyderm](https://docs.pachyderm.com/latest/set-up/on-prem/)

### Proxy

If you are in the HPE internal network, you will need to set up the proxy.
Simply execute the following command:

```bash
export HTTP_PROXY=http://web-proxy.corp.hpecorp.net:8080
export HTTPS_PROXY=http://web-proxy.corp.hpecorp.net:8080
```

If you want to make this permanent, add these lines to the `~/.bashrc` or equivalent file.

### kubectl

Simply following the instructions on the [kubernetes website](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/) should be sufficient.
But for the sake of completeness, here is what I did:

```bash
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
```

If the proxy is giving you grief one can simply download the binary elsewhere and copy it to the target machine. (not recommended)

### Installing minikube

The same things apply for minikube as for kubectl.
The propper instructions can be found on the [minikube website](https://minikube.sigs.k8s.io/docs/start/)
But here is what I did anyway:

```bash
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube_latest_amd64.deb
sudo dpkg -i minikube_latest_amd64.deb
```

We can then test the installation by running:

```bash
minikube start
kubectl cluster-info
```

If you are getting an error stating that it is not able to connect to the cluster you might need to set the following environment variable:

```bash
export NO_PROXY=localhost,127.0.0.1,10.96.0.0/12,192.168.59.0/24,192.168.49.0/24,192.168.39.0/24
```

### Installing [helm](https://helm.sh/docs/intro/install/)

Same procedure as every year...

```bash
curl https://baltocdn.com/helm/signing.asc | gpg --dearmor | sudo tee /usr/share/keyrings/helm.gpg > /dev/null
sudo apt-get install apt-transport-https --yes
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/helm.gpg] https://baltocdn.com/helm/stable/debian/ all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list
sudo apt-get update
sudo apt-get install helm
```

### [Persistent Storage](https://kubernetes.io/docs/tasks/configure-pod-container/configure-persistent-volume-storage/)

We need to create a persistent volume for etcd and the postgres database.
Therefore we need to create a directory for each of them.

```bash
mkdir -p /mnt/pachyderm/etcd
mkdir -p /mnt/pachyderm/postgres
```

We then create the configuration files for the persistent volumes.

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: etcd-pv
labels:
    type: local
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteOnce
  storageClassName: manual
  local:
    path: /mnt/pachyderm/etcd
    
---

apiVersion: v1
kind: PersistentVolume
metadata:
  name: postgres-pv
labels:
    type: local
spec:
    capacity:
        storage: 10Gi
    accessModes:
        - ReadWriteOnce
    storageClassName: manual
    local:
        path: /mnt/pachyderm/postgres
```

And then the corresponding persistent volume claims.

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: etcd-pvc
spec:
    storageClassName: manual
    accessModes:
        - ReadWriteOnce
    resources:
        requests:
        storage: 10Gi

---

apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
spec:
    storageClassName: manual
    accessModes:
        - ReadWriteOnce
    resources:
        requests:
        storage: 10Gi
```

Then we add the storage class to the cluster.

```bash
kubectl apply -f filename.yaml
```

We then take note of the storage class name because we will add it to the helm values file later. \
In this case it is `manual`.

### Installing [MinIO](https://min.io/docs/minio/linux/index.html)

We now install an S3 compatible storage system. Which one does not really matter, but I chose MinIO because it is easy to install and configure.

```bash
wget https://dl.min.io/server/minio/release/linux-amd64/archive/minio_20230619195250.0.0_amd64.deb -O minio.deb
sudo dpkg -i minio.deb

mkdir -p /mnt/pachyderm/minio

# to manually start the server
minio server /mnt/pachyderm/minio --console-address :9001
```

The standard password is `minioadmin:minioadmin`

Then you can access the web interface at `http://localhost:9001` where you should login, change the password and create a bucket. \
The access credentials for the bucket will be added to the helm values file later, so take note of them.

### Installing [Pachyderm](https://docs.pachyderm.com/latest/set-up/on-prem/)

First we need to add the Pachyderm helm repository:

```bash
helm repo add pachyderm https://helm.pachyderm.com
helm repo update
```

We then get the values file from the repository and edit it to our liking.\
My setup is based on the version `2.6.4-1`, so it might be different for future versions.

```bash
wget https://raw.githubusercontent.com/pachyderm/pachyderm/2.6.x/etc/helm/pachyderm/values.yaml  
```

#### MinIO

First we change the deploy target at line `L7`

```yaml
# Deploy Target configures the storage backend to use and cloud provider
# settings (storage classes, etc). It must be one of GOOGLE, AMAZON,
# MINIO, MICROSOFT, CUSTOM or LOCAL.
deployTarget: "MINIO"
...
```

This does not need to be set when using something else but with MinIO we also have to set `L544` to "MINIO"

```yaml
...
storage:
    # backend configures the storage backend to use.  It must be one
    # of GOOGLE, AMAZON, MINIO, MICROSOFT or LOCAL. This is set automatically
    # if deployTarget is GOOGLE, AMAZON, MICROSOFT, or LOCAL
    backend: "MINIO"
    ...
```

A little further down (`L635`) we find the MinIO configuration. We need to set the endpoint, access key and secret key.

This point was a little tricky as I had MinIO installed on the same machine as Pachyderm, but it would take no other value than the outward facing IP address of the machine.

```yaml
...
    minio:
      # minio bucket name
      bucket: "<bucket name>"
      # the minio endpoint. Should only be the hostname:port, no http/https.
      endpoint: "10.X.X.X:9000"
      # the username/id with readwrite access to the bucket.
      id: "<id>"
      # the secret/password of the user with readwrite access to the bucket.
      secret: "<secret>"
      # enable https for minio with "true" defaults to "false"
      secure: "false"   
      # Enable S3v2 support by setting signature to "1". This feature is being deprecated
      signature: ""
      ...
```

#### Storage classes

Now we add the storage classes we created earlier to the Postgres at `L784`

```yaml
...
    # AWS: https://docs.aws.amazon.com/eks/latest/userguide/storage-classes.html
    # GCP: https://cloud.google.com/compute/docs/disks/performance#disk_types
    # Azure: https://docs.microsoft.com/en-us/azure/aks/concepts-storage#storage-classes
    storageClass: manual 
    # storageSize specifies the size of the volume to use for postgresql
    # Recommended Minimum Disk size for Microsoft/Azure: 256Gi  - 1,100 IOPS https://azure.microsoft.com/en-us/pricing/details/managed-disks/
...
```

and for the etcd at around `L144`

```yaml
...

  # GCP: https://cloud.google.com/compute/docs/disks/performance#disk_types
  # Azure: https://docs.microsoft.com/en-us/azure/aks/concepts-storage#storage-classes
  #storageClass: manual
  storageClassName: manual

  # storageSize specifies the size of the volume to use for etcd.
  # Recommended Minimum Disk size for Microsoft/Azure: 256Gi  - 1,100 IOPS https://azure.microsoft.com/en-us/pricing/details/managed-disks/

... 
```

#### SSL Certificates

My setup refuses to work without SSL certificates, so I had to generate some.

```bash
openssl genrsa -out <CertName>.key 2048 
openssl req -new -x509 -sha256 -key <CertName>.key -out <CertName>.crt

kubectl create secret tls <SecretName> --cert=<CertName>.crt --key=<CertName>.key
```

We then edit the `values.yaml` file at around `L683` to use the certificates.

```yaml
...
  tls:
    enabled: true
    secretName: "<SecretName>"
    newSecret:
      create: false
    ...
```

### CLI

To directly interact with the cluster we need to install the Pachyderm CLI.

```bash
curl -o /tmp/pachctl.deb -L https://github.com/pachyderm/pachyderm/releases/download/v2.6.5/pachctl_2.6.5_amd64.deb && sudo dpkg -i /tmp/pachctl.deb
```

### Deploy

Now that the values file is ready we can install Pachyderm.

```bash
helm install pachyderm pachyderm/pachyderm \
  -f ./values.yml pachyderm/pachyderm \
  --set postgresql.volumePermissions.enabled=true \
  --set deployTarget=LOCAL \
  --set proxy.enabled=true \
  --set proxy.service.type=NodePort  \
  --set proxy.host=localhost \
  --set proxy.service.httpPort=8080
  
```

Now you might want to connect to the dashboard. This can be done by port-forwarding the service.

```bash
pachctl port-forward
```

:tada: Now we should be able to access the dashboard at `http://localhost:4000` :tada:

