# Installing Forgejo

## Namespace

As always we create a namespace for the project:

```bash
kubectl create namespace forgejo
```

## Persistent Volumes

We need to create a location for the persistent volume:

```bash
mkdir -p /mnt/forgejo/postgres
mkdir -p /mnt/forgejo/zero
sudo chown -R eckerth:users /mnt/forgejo/      
```

We then create the persistent volume:

```bash
kubectl -n  forgejo apply -f volumes.yaml
```
