###################################################
#                Dependencies                     #
###################################################

# Build stage with SSH keys to clone private repositories
FROM ubuntu:20.04 AS builder

# Define build arguments
ARG DEBUG
ARG REPO_URL
ARG BRANCH_NAME
ARG COMMIT_HASH
ARG SSH_PRIVATE_KEY

ARG HTTP_PROXY
ARG NO_PROXY

# Set environment variables for proxies and non-interactive package installation
ENV DEBIAN_FRONTEND=noninteractive
ENV HTTP_PROXY=$HTTP_PROXY
ENV HTTPS_PROXY=$HTTP_PROXY
ENV NO_PROXY=$NO_PROXY
ENV DEBUG_BUILD_OPTION=$DEBUGz

# Create directories
RUN mkdir -p /workspace/sw/
WORKDIR /workspace/sw


# Install necessary dependencies
RUN apt-get update 
RUN apt-get install -y \
    git=1:2.25.1-1ubuntu3 \
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
RUN git clone --depth 1 --branch $BRANCH_NAME $REPO_URL OpenFAM
WORKDIR /workspace/sw/OpenFAM
RUN git fetch --depth 1 origin $COMMIT_HASH
RUN git checkout $COMMIT_HASH    


###################################################
#                 Build OpenFAM3                  #
###################################################


# Conditional debug build command
WORKDIR /workspace/sw/OpenFAM/third-party

RUN if [ -n "$DEBUG_BUILD_OPTION" ]; then \
        mkdir -p build; \
        touch build/DEBUG; \
    else \
        rm -rf build; \
    fi


# Build third-party dependencies if clean build
RUN ./build.sh --no-package-install


RUN mkdir -p /workspace/sw/OpenFAM/build
WORKDIR /workspace/sw/OpenFAM/build
RUN CC=gcc CXX=g++ cmake .. -DLIBFABRIC_PATH=/opt/cray/libfabric/1.15.2.0/ $DEBUG_BUILD_OPTION
    

RUN make -j install 
RUN ln -sf ../tools/openfam_adm.py bin/openfam_adm

###################################################
#                 Final Stage                     #
###################################################

# Final stage without SSH keys
FROM ubuntu:20.04

# Setting up proxy
ENV HTTP_PROXY=$HTTP_PROXY
ENV HTTPS_PROXY=$HTTP_PROXY
ENV NO_PROXY=$NO_PROXY

RUN mkdir -p /workspace/sw/OpenFAM
WORKDIR /workspace/sw

# Copy over necessary dependencies and files from the builder stage
COPY --from=builder /workspace/sw/ /workspace/sw/

WORKDIR /workspace/sw/OpenFAM

# Set environment variables for non-interactive package installation
ENV DEBIAN_FRONTEND=noninteractive

# Set default command for running the container
CMD ["bash sleep infinity"]