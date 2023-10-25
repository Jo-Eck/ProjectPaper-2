
# Arkouda

Based on the helm charts in the [Arkouda Contrip repository](https://github.com/Bears-R-Us/arkouda-contrib/tree/main/arkouda-helm-charts),
we can now start to deploy Arkouda in our kubernetes Kluster.
These installation instructions are based on the readme of the same repo.

```bash
git clone git@github.com:Bears-R-Us/arkouda-contrib.git
```

## Namespace

For this we create its own namespace.

```bash
kubectl create namespace arkouda
```

If you want to make your live a little bit easier and work with many differnt namespaces, you can add the following alias to your `.bashrc` or `.zshrc` file.

```bash
alias kark='kubectl --namespace arkouda'
```

This keeps you from having to type `--namespace arkouda` or `-n arkouda` every time you want to interact with the arkouda namespace.

## Secrets

To get the containers to to talk to each other and to interface with the kubernetes api we need to create some secrets.

### SSH

The first secret we create is the ssh secret. This is used to connect to the pods and to the kubernetes api. \
As requested by the [dokumentation](https://github.com/Bears-R-Us/arkouda-contrib/tree/3e4050bfef2bf2a24c7418bb1115996b37637e25/arkouda-helm-charts/arkouda-udp-server#ssh-secret), this ssh key needs to be created while impersonating a user with the `ubuntu` username.

```bash
adduser ubuntu --disabled-password --gecos ""
su ubuntu -c "ssh-keygen -t rsa -b 4096 -C \"ubuntu@arkouda\" -f ~/id_rsa -q -N \"\""

# then we create the secret
kark create secret generic arkouda-ssh --from-file=id_rsa=./id_rsa --from-file=id_rsa.pub=./id_rsa.pub
```

### SSL

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

### Cluster Role

The following section is an excerpt of the  [Arkouda UDP Server documentation](https://github.com/Bears-R-Us/arkouda-contrib/tree/3e4050bfef2bf2a24c7418bb1115996b37637e25/arkouda-helm-charts/arkouda-udp-server#clusterroles).

## ClusterRoles

The Kubernetes API permissions are in the form of a ClusterRole (scoped to all namespaces). For the purposes of this demonstration, the ClusterRoles are as follows. Corresponding Role definitions only differ in that that the Kind field is Role and metadata has a namespace element.

### GASNET udp Integration

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

### Service Integration

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

## Locale-Pods

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

# Pachykouda - Client

Now we have to create an image which enables pachyderm to send messages to the arkouda cluster.
To accomplish this we need to create a docker image which contains the arkouda client, takes the arkouda server ip and arbitrary arkouda commands as arguments and then executes the commands on the server.

## Local Registry

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
