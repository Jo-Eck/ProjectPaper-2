# This file is to document my bash command to build the container:

docker build -t heydar20.labs.hpecorp.net:31320/custom-jenkins \
        -f custom_jenkins.dockerfile \
        --build-arg HTTP_PROXY="http://proxy.its.hpecorp.net:80" \
        --build-arg NO_PROXY="localhost,cluster.local,.cluster.local,.labs.hpecorp.net,127.0.0.1,192.168.0.0/16,10.0.0.0/8,172.16.0.0/12,10.244.0.0/16,10.96.0.0/12,10.93.0.0/16,10.152.0.0/16" .
docker push heydar20.labs.hpecorp.net:31320/custom-jenkins
