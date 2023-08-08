FROM bearsrus/chapel-gasnet-smp:1.30.0  AS builder

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

USER root

ENV LIBFABRIC_DIR=/root/sw/OpenFAM3/third-party/build
ENV CHAPEL_BUILDS=/root/sw/



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
    curl \
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

RUN git clone --branch hkuno/sles-1 git@github.hpe.com:jon-eckerth/chpltools


WORKDIR /root/sw
RUN git clone --depth 1 --branch 1.30.0_openfam3.1 ssh://git@github.hpe.com/john-l-byrne/chapel-fam OpenFAM3
WORKDIR /root/sw/OpenFAM3
RUN git fetch --depth 1 origin 1b3cfbdfb7666c12dd9470ebf0b1032d9d7354b7
RUN git checkout 1b3cfbdfb7666c12dd9470ebf0b1032d9d7354b7  


WORKDIR /root/sw
RUN git clone --depth 1 --branch john.l.byrne/v2023.05.05.fam git@github.hpe.com:john-l-byrne/arkouda arkouda
WORKDIR /root/sw/arkouda
RUN git fetch --depth 1 origin d7b5cb30123973838d573323bddc8c8fd364a658
RUN git checkout d7b5cb30123973838d573323bddc8c8fd364a658  
    
## Described by notes.md

RUN /root/sw/chpltools/mfam.sh -c 

RUN make install-deps

RUN /root/sw/chpltools/max.sh -c chplgasnet
