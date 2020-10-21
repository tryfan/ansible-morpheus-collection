FROM willhallonline/ansible:2.10-centos-7
COPY *.tar.gz /
RUN ansible --version
RUN ansible-galaxy collection install /morpheusdata-morpheus-0.0.1.tar.gz -p /usr/share/ansible/collections
ENTRYPOINT [ "/bin/bash" ]