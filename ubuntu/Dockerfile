FROM ubuntu:20.04
RUN apt update && \
    apt install ssh -y
COPY ./sshd_config /etc/ssh/
RUN echo "root:kingping" | chpasswd
RUN useradd -rm -d /home/user -s /bin/bash -g root -G sudo -u 1001 -p $(openssl passwd -1 kingping) user

