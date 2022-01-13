FROM redhat/ubi8
RUN yum install openssh-server net-tools nc openssl -y
COPY ./sshd_config /etc/ssh/
RUN echo "root:kingping" | chpasswd
RUN useradd -rm -d /home/user -s /bin/bash -g root -G wheel -u 1001 -p $(openssl passwd -1 kingping) user

