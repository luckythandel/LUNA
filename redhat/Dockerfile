FROM redhat/ubi8
RUN yum install openssh-server net-tools nc openssl initscripts -y
COPY ./sshd_config /etc/ssh/
COPY ./banner /etc/.banner
RUN echo "root:kingping" | chpasswd
RUN yum install vim nano -y
COPY ./service /usr/sbin/service
RUN chmod +x /usr/sbin/service
RUN ssh-keygen -A
RUN useradd -rm -d /home/user -s /bin/bash -g root -G wheel -u 1001 -p $(openssl passwd -1 kingping) user

