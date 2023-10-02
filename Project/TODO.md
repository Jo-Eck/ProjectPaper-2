# TODO

## Before I leave

- [ ] Moving minio to big hard drive
- [ ] including business license
- [X] more documentation
- [X] convert minio to systemd service
- [X] harumi kubeconf (sudo user can copy it as described in README)
- [X] Harumi access jenkins pipeline

## Functionality

- [ ] Arkouda with OpenFam

- [ ] Jenkins Pipline reliability
  - [ ] Maybe redesign?
  - [ ] Restructuring
  - [ ] Investigating deeper lexical analysis

- [ ] Jenkins make Repos declarative
  - [ ] Keeping the forgejo repo in sync with the Pachyderm repo
  - [ ] When removing items from forgejo remove them from the Pachyderm repo

## QOL (nice to have)

- [  ] Jenkins sends current build status to forgejo
  - [ ] Status updates
  - [ ] Build fail error code

- [ ] Forgejo designated tags for different executions
  - [ ] Repos which are to be ignored
  - [ ] Repos which are examples ...

- [ ] Combined Helm Chart for all services
  - [ ] Jenkins
  - [ ] Pachyderm
  - [ ] Forgejo
  - [ ] Docker Registry

## Infrastructure (if cluster is rebuild)

- [ ] Replacing Minio with distributed storage
  - [ ] Ceph + Rook

- [ ] automated certificate management
  - [ ] Vault

- [ ] Monitoring
  - [ ] Prometheus
  - [ ] Grafana

- [ ] Permission integration with HPE via (Radius/LDAP/AD)
  - [ ] Jenkins
  - [ ] Pachyderm(Business)
  - [ ] Forgejo
  - [ ] SSO for all services

## Intersting future projects

- [ ] Moving over to singularity
- [ ] Redesigning network layer
  - [ ] Investigation needed
  - [ ] Moving over to Pod to Pod communication
- [ ] Complete integration with notebooks
  - [ ] One Notebook becomes a workflow
  - [ ] Each cell becomes a step
    - [ ] Incredible fit with FAM
