# Setting up the GitOps CI/CD

This part is concerned wit setting up both the Version Control System Forgejo and the CI/CD system Jenkins. \
While Forgeo is a fork of Gitea, it is still sparcely documented and thus we will not setup the runner system of Forgejo, but instead use Jenkins for CI/CD.


## Namespaces

As always we create namespaces to keep things clean:

```bash
kubectl create namespace forgejo
kubectl create namespace jenkins
```

## Persistent Volumes

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

## Installation

After these are applied we can simply install the helm chart:

```bash
helm repo add jenkins https://charts.jenkins.io
helm repo update
helm install -n jenkins jenkins jenkins/jenkins -f ./jenkins/values.yaml
helm install -n forgejo forgejo oci://codeberg.org/forgejo-contrib/forgejo -f ./forgejo/values.yaml 
```

## Configuring

To connect jenkins with our Forgejo config, we hae to change a couple of things [nedds to be rewritten]:

1. adding config mapt to forgejo:

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

and apply it:

```bash
kubectl -n forgejo apply -f ./forgejo/configmap.yaml
```

2. jenkins plugins:

```yaml
 - kubernetes:3937.vd7b_82db_e347b_
 - workflow-aggregator:596.v8c21c963d92d
 - job-dsl:1.84
 - gitea:1.4.5
 - docker-workflow:1.26
 - git:5.1.0
 - envinject-api:1.199.v3ce31253ed13
 - ssh-credentials:308.ve4497b_ccd8f4
 - configuration-as-code:1647.ve39ca_b_829b_42
 - github-api:1.314-431.v78d72a_3fe4c3
 - generic-webhook-trigger:1.86.5
```


## Setting up the CI/CD in jenkins

the pipeline is as follows
```bash
# Extract info from the payload (Assuming webhook payload structure remains as earlier discussed)
REPO_NAME=$(echo $payload | jq -r '.repository.name')
CHANGED_FILES=$(git diff --name-only HEAD~1..HEAD)  # Lists files changed in the last commit

# Initialize flags
DOCKER_BUILD=false
REPO_UPDATE=false
PIPELINE_UPDATE=false

# Check which files changed
for file in $CHANGED_FILES; do
    if [[ $file == *_code.* ]]; then
        DOCKER_BUILD=true
    elif [[ $file == *_repo.yaml ]]; then
        REPO_UPDATE=true
    elif [[ $file == *_pipeline.yaml ]]; then
        PIPELINE_UPDATE=true
    fi
done

# Save flags to properties file
echo "DOCKER_BUILD=$DOCKER_BUILD" > action_flags.properties
echo "REPO_UPDATE=$REPO_UPDATE" >> action_flags.properties
echo "PIPELINE_UPDATE=$PIPELINE_UPDATE" >> action_flags.properties
```

```groovy
if (env.DOCKER_BUILD == "true") {
    job("${REPO_NAME}-docker-build") {
        steps {
            shell('''
                # Set the Docker image name and registry
                IMAGE_NAME="my-docker-registry.com/${REPO_NAME}:latest"

                # Create a Dockerfile if it doesn't exist
                if [ ! -f Dockerfile ]; then
                    echo "FROM ubuntu:latest" > Dockerfile
                    echo "RUN apt-get update && apt-get install -y python3" >> Dockerfile
                    echo "ADD ./*.py /app/" >> Dockerfile
                    echo "WORKDIR /app" >> Dockerfile
                    echo "CMD [\"python3\", \"./${REPO_NAME}_code.py\"]" >> Dockerfile
                fi

                # Build the Docker image
                docker build -t $IMAGE_NAME .

                # Push the Docker image to the registry
                docker push $IMAGE_NAME
            ''')
        }
    }
}
if (env.REPO_UPDATE == "true") {
    job("${REPO_NAME}-repo-deploy") {
        steps {
            shell('''
                # Create the Pachyderm repository
                pachctl create repo ${REPO_NAME}

                # Assuming the YAML has a reference to the data, use it to populate the repo
                DATA_PATH=$(cat ${REPO_NAME}_repo.yaml | grep dataPath | cut -d ':' -f2)
                pachctl put file ${REPO_NAME}@master -i $DATA_PATH
            ''')
        }
    }
}
if (env.PIPELINE_UPDATE == "true") {
    job("${REPO_NAME}-pipeline-deploy") {
        steps {
            shell('''
                # Deploy the Pachyderm pipeline
                pachctl create pipeline -f ${REPO_NAME}_pipeline.yaml
            ''')
        }
    }
}
```