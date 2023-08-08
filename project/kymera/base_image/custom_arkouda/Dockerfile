###################################################
#                Dependencies                     #
###################################################

# Build stage with SSH keys to clone private repositories
FROM heydar20.labs.hpecorp.net:31320/custom_chapel AS builder

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

# Install necessary dependencies
RUN apt-get update 
RUN apt-get install -y \
    build-essential \
    git \
    curl \
    libre2-dev \
    gcc \
    hdf5-tools\
    python3-dev \
    gzip \
    ssh \
    && rm -rf /var/lib/apt/lists/*


# Set up SSH keys
RUN  mkdir /root/.ssh/ && \
    echo "${SSH_PRIVATE_KEY}" > /root/.ssh/id_rsa && \
    chmod 600 /root/.ssh/id_rsa && \
    ssh-keyscan -H github.hpe.com > /root/.ssh/known_hosts

# Create directories
RUN mkdir -p /workspace/sw/
WORKDIR /workspace/sw

###################################################
#                  Clone Arkouda                  #
###################################################


# Clone repositories
WORKDIR /workspace/sw
RUN git clone --depth 1 --branch $BRANCH_NAME $REPO_URL arkouda
WORKDIR /workspace/sw/arkouda

RUN git fetch --depth 1 origin $COMMIT_HASH
RUN git checkout $COMMIT_HASH    


###################################################
#                  Build Arkouda                  #
###################################################

ENV CHPL_HOME=/workspace/sw/chapel
ENV ARKOUDA_DEVELOPER=1
ENV ARKOUDA_QUICK_COMPILE=1
ENV ARKOUDA_SKIP_CHECK_DEPS=1


RUN make V=1 -j