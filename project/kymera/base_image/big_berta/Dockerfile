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
    strace \
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

WORKDIR /root/sw

RUN git clone --branch hkuno/sles-1 ssh://git@github.hpe.com/harumi-kuno/chpltools

RUN /root/sw/chpltools/check_out_src.sh

ENV CHAPEL_BUILDS=/root/sw/

## Described by notes.md

RUN /root/sw/chpltools/mfam.sh -c 



ENV LIBFABRIC_DIR=/root/sw/OpenFAM3/third-party/build

RUN apt update && apt upgrade -y && apt install tree

RUN /root/sw/chpltools/mcx.sh -c chplofi

RUN cat /root/sw/chplofi/make.out

RUN bash /root/sw/chapel/util/setchplenv.bash

RUN apt install -y curl

ENV CHPL_LAUNCHER=none

RUN /root/sw/chpltools/max.sh -c chplofi