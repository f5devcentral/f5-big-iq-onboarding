FROM ubuntu:latest

RUN apt-get update && \
    apt-get install -y python python-dev python-pip python-jmespath && \
    apt-get install -y openssh-client iputils-ping sshpass

RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN pip install ansible  

RUN ansible-galaxy install f5devcentral.f5ansible,master && \
    ansible-galaxy install f5devcentral.bigiq_onboard && \
    ansible-galaxy install f5devcentral.register_dcd

RUN mkdir /etc/ansible/
COPY ansible.cfg /etc/ansible/ansible.cfg