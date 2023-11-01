FROM jenkins/jenkins:lts-jdk11
USER root

ARG HTTP_PROXY
# HTTP_PROXY="http://proxy.its.hpecorp.net:80" \
ARG NO_PROXY
# NO_PROXY="localhost,cluster.local,.cluster.local,.labs.hpecorp.net,127.0.0.1,192.168.0.0/16,10.0.0.0/8,172.16.0.0/12,10.244.0.0/16,10.96.0.0/12,10.93.0.0/16,10.152.0.0/16" .


ENV HTTP_PROXY=$HTTP_PROXY
ENV HTTPS_PROXY=$HTTP_PROXY
ENV http_proxy=$HTTP_PROXY
ENV https_proxy=$HTTP_PROXY
ENV NO_PROXY=$NO_PROXY
ENV DEBUG_BUILD_OPTION=$DEBUG


RUN apt-get update && apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    tree \
    gnupg \
    software-properties-common \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*


RUN curl -o /tmp/pachctl.deb -L https://github.com/pachyderm/pachyderm/releases/download/v2.6.5/pachctl_2.6.5_amd64.deb && dpkg -i /tmp/pachctl.deb

COPY ./requirements.txt ./requirements.txt 

# gitdb==4.0.10
# GitPython==3.1.32
# Pygments==2.16.1
# smmap==5.0.0
# gitignore-parser==0.1.6
# python-pachyderm==7.6.0
# pyyaml==5.4.1

RUN pip install -r ./requirements.txt 
RUN rm ./requirements.txt

USER jenkins
