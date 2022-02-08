FROM kalilinux/kali-rolling
RUN apt update && \
    apt install ssh nano vim net-tools netcat-openbsd tmux -y && \
    apt install openssl -y
COPY ./sshd_config /etc/ssh/
COPY ./banner /etc/.banner
RUN echo "root:kingping" | chpasswd
RUN apt install gdb -y
RUN useradd -rm -d /home/user -s /bin/bash -g root -G sudo -u 1001 -p $(openssl passwd -1 kingping) user

