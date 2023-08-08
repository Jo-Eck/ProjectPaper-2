FROM ubuntu:20.04 AS builder

# Define build arguments

ARG SSH_PRIVATE_KEY

# Set environment variables for proxies and non-interactive package installation
ENV DEBIAN_FRONTEND=noninteractive

# Create directories
RUN mkdir -p ~/sw

ENV HTTP_PROXY="http://proxy.its.hpecorp.net:80"
ENV HTTPS_PROX=HTTP_PROXY
ENV http_proxy=$HTTP_PROXY
ENV https_proxy=$HTTP_PROXY

# Install necessary dependencies
RUN apt-get update 
RUN apt-get install -y \
    git \
    libfabric-dev \
    libyaml-cpp-dev \
    cmake \
    g++ \
    ca-certificates \
    flex \
    cmake \
    gcc \
    g++ \
    libgmp10 \
    libgmp-dev \
    libpmem-dev \
    libnuma-dev \
    locales \
    make \
    mawk \
    file \
    pkg-config \
    openssh-client \
    openssh-server \
    procps \
    dnsutils \
    hdf5-tools \
    libcurl4-openssl-dev \
    clang \
    libboost-all-dev \
    lldb \
    lld \
    llvm-dev \
    gcc \
    openssl \
    libssl-dev \
    make \
    && rm -rf /var/lib/apt/lists/*

# Set up SSH keys
RUN mkdir /root/.ssh/ && \
    echo "${SSH_PRIVATE_KEY}" > /root/.ssh/id_rsa && \
    chmod 600 /root/.ssh/id_rsa && \
    ssh-keyscan -H github.hpe.com > /root/.ssh/known_hosts

# Clone repositories

WORKDIR /workspace/sw
RUN git clone --depth 1 --branch 1.30.0_openfam3.1 ssh://git@github.hpe.com/john-l-byrne/chapel-fam OpenFAM
WORKDIR /workspace/sw/OpenFAM
RUN git fetch --depth 1 origin aaed960c948838adeaa4e04a4cff61675998a1d0
RUN git checkout aaed960c948838adeaa4e04a4cff61675998a1d0  


WORKDIR /workspace/sw
RUN git clone --depth 1 --branch 1.30.0_openfam3.1 ssh://git@github.hpe.com/john-l-byrne/chapel-fam Chapel
WORKDIR /workspace/sw/Chapel
RUN git fetch --depth 1 origin b3cfbdfb7666c12dd9470ebf0b1032d9d7354b7
RUN git checkout b3cfbdfb7666c12dd9470ebf0b1032d9d7354b7  

WORKDIR /workspace/sw
RUN git clone --depth 1 --branch john.l.byrne/v2023.05.05.fam ssh://git@github.hpe.com/john-l-byrne/arkouda Arkouda
WORKDIR /workspace/sw/Arkouda
RUN git fetch --depth 1 origin d7b5cb30123973838d573323bddc8c8fd364a658
RUN git checkout d7b5cb30123973838d573323bddc8c8fd364a658  

ENV CHAPEL_BUILDS=/workspace/sw/

## Described by notes.md

RUN /root/sw/chpltools/mfam.sh -c 

ENV LIBFABRIC_DIR=/root/sw/OpenFAM3/third-party/build


RUN /root/sw/chpltools/mcx.sh -c chplofi

RUN source /root/sw/chplofi/setchplenv.bash

RUN /root/sw/chpltools/max.sh -c chplofi