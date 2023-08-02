#!/bin/bash

# Build custom openfam image

docker build \
  --build-arg SSH_PRIVATE_KEY="$(cat ./id_rsa)" \
  --build-arg HTTP_PROXY="http://proxy.its.hpecorp.net:80" \
  --build-arg NO_PROXY="localhost,127.0.0.1,10.0.0.0/8,172.16.0.0/16,10.93.246.68/28"\
  \
  --build-arg REPO_URL="ssh://git@github.hpe.com/john-l-byrne/OpenFAM" \
  --build-arg BRANCH_NAME="john.l.byrne/3_1" \
  --build-arg COMMIT_HASH="aaed960c948838adeaa4e04a4cff61675998a1d0" \
  \
  -t custom_fam:3.1 ./custom_fam 2>&1 | tee -a build.log


# Building chapel image on the top of opemfam image
docker build \
  --build-arg SSH_PRIVATE_KEY="$(cat ./id_rsa)" \
  --build-arg HTTP_PROXY="http://proxy.its.hpecorp.net:80" \
  --build-arg NO_PROXY="localhost,127.0.0.1,10.0.0.0/8,172.16.0.0/16,10.93.246.68/28"\
  \
  --build-arg REPO_URL="ssh://git@github.hpe.com/john-l-byrne/chapel-fam" \
  --build-arg BRANCH_NAME="1.30.0_openfam3.1" \
  --build-arg COMMIT_HASH="1b3cfbdfb7666c12dd9470ebf0b1032d9d7354b7" \
  \
  -t custom_chapel:1.30.0 ./custom_chapel

# Building baseline_arkouda image on the top of opemfam image

