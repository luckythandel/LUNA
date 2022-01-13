FROM kalilinux/kali-rolling
RUN apt update && \
    apt install ssh net-tools netcat-openbsd tmux -y && \
    apt install openssl -y
COPY ./sshd_config /etc/ssh/
RUN echo "root:kingping" | chpasswd
RUN useradd -rm -d /home/user -s /bin/bash -g root -G sudo -u 1001 -p $(openssl passwd -1 kingping) user

