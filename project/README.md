# Installation instructions

## Pachyderm

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
Therefore we need to create a directory for each of them. and change the owner to the user `nobody`.

```bash
sudo mkdir -p /mnt/pachyderm/etcd
sudo mkdir -p /mnt/pachyderm/postgres

sudo chown -R nobody:nogroup /mnt/pachyderm
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

<!-- #### SSL Certificates

This breaks the connection of the proxy to the pachd server.
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
``` -->

### CLI

To directly interact with the cluster we need to install the Pachyderm CLI.

```bash
curl -o /tmp/pachctl.deb -L https://github.com/pachyderm/pachyderm/releases/download/v2.6.5/pachctl_2.6.5_amd64.deb && sudo dpkg -i /tmp/pachctl.deb
```

### Deploy

Now that the values file is ready we can install Pachyderm.

```bash
helm install pachyderm -n pachyderm pachyderm/pachyderm \
  -f ./values.yaml pachyderm/pachyderm \
  --set postgresql.volumePermissions.enabled=true \
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

---

## Arkouda

Based on the helm charts in the [Arkouda Contrip repository](https://github.com/Bears-R-Us/arkouda-contrib/tree/main/arkouda-helm-charts),
we can now start to deploy Arkouda in our kubernetes Kluster.

```bash
git clone git@github.com:Bears-R-Us/arkouda-contrib.git
```

### Namespace

For this we create its own namespace.

```bash
kubectl create namespace arkouda
```

If you want to make your live a little bit easier and work with many differnt namespaces, you can add the following alias to your `.bashrc` or `.zshrc` file.

```bash
alias kark='kubectl --namespace arkouda'
```

This keeps you from having to type `--namespace arkouda` or `-n arkouda` every time you want to interact with the arkouda namespace.

### Secrets

To get the containers to to talk to each other and to interface with the kubernetes api we need to create some secrets.

#### SSH

The first secret we create is the ssh secret. This is used to connect to the pods and to the kubernetes api. \
As requested by the [dokumentation](https://github.com/Bears-R-Us/arkouda-contrib/tree/3e4050bfef2bf2a24c7418bb1115996b37637e25/arkouda-helm-charts/arkouda-udp-server#ssh-secret), this ssh key needs to be created while impersonating a user with the `ubuntu` username.

```bash
adduser ubuntu --disabled-password --gecos ""
su ubuntu -c "ssh-keygen -t rsa -b 4096 -C \"ubuntu@arkouda\" -f ~/id_rsa -q -N \"\""

# then we create the secret
kark create secret generic arkouda-ssh --from-file=id_rsa=./id_rsa --from-file=id_rsa.pub=./id_rsa.pub
```

#### SSL

The second secret we need is a ssl secret. This is used to connect to the Kubernetes API. \
This secret is created by generating a self signed certificate.

```bash

# we start by generating the certificate
# note do not change the name of the certificate, as it is hardcoded in the yaml file
openssl genrsa -out tls.key 2048

# creating the certificate signing request
openssl req -new -key tls.key -out tls.csr -subj "/CN=arkouda/O=group1"


# now we create a CSR object in the kubernetes api

cat <<EOF | kark apply -f -
apiVersion: certificates.k8s.io/v1
kind: CertificateSigningRequest
metadata:
  name: arkouda
spec:
  request: $(cat tls.csr | base64 | tr -d '\n')
  signerName: kubernetes.io/kube-apiserver-client
  usages:
  - digital signature
  - key encipherment
  - client auth
EOF

# and get it approved by an admin
kark certificate approve arkouda


# from this we get the certificate
kark get csr arkouda -o jsonpath='{.status.certificate}' | base64 --decode > tls.crt

# now we can verify whether the certificate is valid (this is specific to minikube)
curl --cacert /home/<your username>/.minikube/ca.crt --cert ./tls.crt --key ./tls.key https://$(minikube ip):8443/api/


# and create the secret
kark create secret generic arkouda-tls --from-file=tls.crt=./tls.crt --from-file=tls.key=./tls.key 
```

#### Cluster Role

The following section is an excerpt of the  [Arkouda UDP Server documentation](https://github.com/Bears-R-Us/arkouda-contrib/tree/3e4050bfef2bf2a24c7418bb1115996b37637e25/arkouda-helm-charts/arkouda-udp-server#clusterroles).

### ClusterRoles

The Kubernetes API permissions are in the form of a ClusterRole (scoped to all namespaces). For the purposes of this demonstration, the ClusterRoles are as follows. Corresponding Role definitions only differ in that that the Kind field is Role and metadata has a namespace element.

#### GASNET udp Integration

The arkouda-udp-server deployment discovers all arkouda-udp-locale pods on startup to create the GASNET udp connections between all Arkouda locales. Accordingly, Arkouda requires Kubernetes pod list and get permissions. The corresponding ClusterRole is as follows:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: arkouda-pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list"]
```

This ClusterRole is bound to the arkouda Kubernetes user as follows:

```yaml
kind: ClusterRoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: arkouda-pod-reader-binding
subjects:
- kind: User
  name: arkouda
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

#### Service Integration

Arkouda-on-Kubernetes integrates with Kubernetes service discovery by creating a Kubernetes service upon arkouda-udp-server startup and deleting the Kubernetes service upon teardown. Consequently, Arkouda-on-Kubernetes requires full Kubernetes service CRUD permissions to enable service discovery. The corresponding ClusterRole is as follows:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: service-endpoints-crud
rules:
- apiGroups: [""]
  resources: ["services","endpoints"]
  verbs: ["get","watch","list","create","delete","update"]
```

This ClusterRole is bound to the arkouda Kubernetes user as follows:

```yaml
kind: ClusterRoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: arkouda-service-endpoints-crud
subjects:
- kind: User
  name: arkouda
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: service-endpoints-crud
  apiGroup: rbac.authorization.k8s.io
```

### Locale-Pods

Now we can edit the `arkouda-udp-locale.yaml` file to match our needs. \
For reference, the following is the configuration on my test setup.

```yaml
######################## Pod Settings ########################

imageRepository: bearsrus
releaseVersion: v2023.05.05
imagePullPolicy: IfNotPresent

resources:
  limits:
    cpu: 1000m
    memory: 1024Mi
  requests:
    cpu: 1000m
    memory: 1024Mi

################ Arkouda Locale Configuration ################

server: 
  port: # Arkouda port, defaults to 5555
  memTrack: true
  numLocales: 4
  threadsPerLocale: 4
external:
  persistence: 
    enabled: false
    path: /arkouda-files # pod directory path, must match arkouda-udp-server 
    hostPath: /mnt/arkouda # host directory path, must match arkouda-udp-server
secrets:
  tls: arkouda-tls # name of tls secret used to access Kubernetes API
  ssh: arkouda-ssh # name of ssh secret used to launch Arkouda locales
```

These can be deployed by moving into the `arkouda-helm-charts` dir and running the following command:

```bash
helm install -n arkouda arkouda-locale arkouda-udp-locale/
```

### Arkouda-Server

Same goes for the `arkouda-udp-server.yaml` file. \
For reference, the following is the configuration on my test setup.
(to find out what the `k8sHost` is, run `kubectl cluster-info`)

```yaml
resources:
  limits:
    cpu: 1000m
    memory: 1024Mi
  requests:
    cpu: 1000m
    memory: 1024Mi

######################## Pod Settings ########################

imageRepository: bearsrus
releaseVersion: v2023.05.05
imagePullPolicy: IfNotPresent

################ Arkouda Driver Configuration ################

server: 
  numLocales: 1 # total number of Arkouda locales = number of arkouda-udp-locale pods + 1
  authenticate: false # whether to require token authentication
  verbose: true # enable verbose logging
  threadsPerLocale: 5 # number of cpu cores to be used per locale
  memMax: 2000 # maximum bytes of RAM to be used per locale
  memTrack: true
  logLevel: LogLevel.DEBUG
  service:
    type: ClusterIP # k8s service type, usually ClusterIP, NodePort, or LoadBalancer
    port: # k8s service port Arkouda is listening on, defaults to 5555
    nodeport: # if service type is Nodeport
    name: # k8s service name
  metrics:
    collectMetrics: false # whether to collect metrics and make them available via  k8s service
    service:
      name: # k8s service name for the Arkouda metrics service endpoint
      port: # k8s service port for the Arkouda metrics service endpoint, defaults to 5556
      targetPort: # k8s targetPort mapping to the Arkouda metrics port, defaults to 5556
locale:
  appName: arkouda-locale
  podMethod: GET_POD_IPS
external:
  persistence:
    enabled: true
    path: /opt/locale # pod directory path, must match arkouda-udp-locale
    hostPath: /mnt/arkouda # host machine path, must match arkouda-udp-locale
  k8sHost: https://192.168.49.2:8443
  namespace: arkouda # namespace Arkouda will register service
  service:
    name: arkoudaserver # k8s service name Arkouda will register
    port: # k8s service port Arkouda will register, defaults to 5555
metricsExporter:
  imageRepository: bearsrus
  releaseVersion: v2023.05.05 # prometheus-arkouda-exporter release version
  imagePullPolicy: IfNotPresent
  service:
    name: # prometheus-arkouda-exporter service name
    port: 5080 # prometheus-arkouda-exporter service port, defaults to 5080
  pollingIntervalSeconds: 5
secrets:
  tls: arkouda-tls # name of tls secret used to access Kubernetes API
  ssh: arkouda-ssh # name of ssh secret used to launch Arkouda locales
```

Which can be deployed by moving into the `arkouda-helm-charts` dir and running the following command:

```bash
helm install -n arkouda arkouda-server arkouda-udp-server/
```

Horray! We now have a working Arkouda cluster running in our kubernetes cluster.

## Pachykouda - Client

Now we have to create an image which enables pachyderm to send messages to the arkouda cluster.
To accomplish this we need to create a docker image which contains the arkouda client, takes the arkouda server ip and arbitrary arkouda commands as arguments and then executes the commands on the server.

### Local Registry

To be able to develop and deploy this image locally, we need to set up a local docker registry within the kubernetes cluster.

```bash
sudo mkdir -p /mnt/registry/certs

# create the certificate

sudo openssl req -newkey rsa:4096 -nodes -sha256 -keyout /mnt/registry/certs/registry.key -addext "subjectAltName = DNS:master-node-k8" -x509 -days 365 -out /mnt/registry/certs/registry.crt

sudo chown -R nobody:nogroup /mnt/registry
```

Now if you want to push or pull from this repository you need to add the certificate to your trusted certificates.

```bash
sudo -S bash -c 'openssl s_client -showcerts -connect heydar20.labs.hpecorp.net:31320 </dev/null 2>/dev/null | openssl x509 -outform PEM > /tmp/heydar20.labs.hpecorp.net.pem && mkdir -p /etc/docker/certs.d/heydar20.labs.hpecorp.net:31320 && cp /tmp/heydar20.labs.hpecorp.net.pem /etc/docker/certs.d/heydar20.labs.hpecorp.net:31320/ca.crt && systemctl restart docker'
```
