###################################################
#                Dependencies                     #
###################################################

# Build stage with SSH keys to clone private repositories
FROM heydar20.labs.hpecorp.net:31320/custom_fam:3.1  AS builder

# Define build arguments
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

ENV CHPL_LLVM="bundled"
ENV CHPL_DEVELOPER=1
ENV OPENFAM_ROOT="/workspace/sw/OpenFAM"

# Install necessary dependencies
RUN apt-get update 
RUN apt-get install -y \
    build-essential \
    python3-venv \
    python3-pip \
    python3-dev \
    git=1:2.25.1-1ubuntu3 \
    openssh-client \
    cmake \
    doxygen \
    openssh-server \
    && rm -rf /var/lib/apt/lists/*


# Set up SSH keys
RUN mkdir /root/.ssh/ && \
    echo "${SSH_PRIVATE_KEY}" > /root/.ssh/id_rsa && \
    chmod 600 /root/.ssh/id_rsa && \
    ssh-keyscan -H github.hpe.com > /root/.ssh/known_hosts

# Create directories
RUN mkdir -p /workspace/sw/
WORKDIR /workspace/sw


# Clone repositories
WORKDIR /workspace/sw
RUN git clone --depth 1 --branch $BRANCH_NAME $REPO_URL chapel
WORKDIR /workspace/sw/chapel

RUN git fetch --depth 1 origin $COMMIT_HASH
RUN git checkout $COMMIT_HASH    

RUN mkdir -p /workspace/sw/chapel/compilat



###################################################
#                   Build Chapel                  #
###################################################

RUN ./configure --prefix="./compilat"
RUN make -j V=1
RUN make install
RUN make c2chapel
RUN echo "***" $(date)