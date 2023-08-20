FROM jenkins/jenkins:lts-jdk11
USER root

ARG HTTP_PROXY
ARG NO_PROXY

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
    gnupg \
    software-properties-common \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*


RUN curl -o /tmp/pachctl.deb -L https://github.com/pachyderm/pachyderm/releases/download/v2.6.5/pachctl_2.6.5_amd64.deb && dpkg -i /tmp/pachctl.deb

COPY ./requirements.txt ./requirements.txt 

RUN pip install -r ./requirements.txt 
RUN rm ./requirements.txt

USER jenkins
