#!/bin/env python3
import socket
import subprocess
import json
import random
from py_console import console
import sys
from pexpect import pxssh

help_menu = """./client.py <server_addr> <port>"""
choices = '''
(1.) Ubuntu
(2.) RedHat 
(3.) Kali 
'''
if(len(sys.argv) < 3):
    console.warn("Host: 127.0.0.1 </> PORT: 1337")
    HOST = "127.0.0.1"
    PORT = 1337
else:
    HOST = sys.argv[1]
    PORT = sys.argv[2]

def send_ack(conn):
    seq = str(random.randint(8000, 9000)).encode()
    conn.send(seq)
    ack = int(conn.recv(1024).decode())
    if(int(seq.decode()) + 1 == ack):
        return True
    return False

def ack_seq(conn):
    ack = int(conn.recv(1024).decode())
    seq = ack + 1
    conn.send(str(seq).encode())
    return

def ssh_shell(container_id, container_ip, username="user", password="kingping", port=22):
    try:
        io = pxssh.pxssh()
        io.login(container_ip, username=username, password=password, port=22)
        console.success("Logged in Successfully, press enter to continue")
        io.interact()
    except Exception as e:
        io.close()
        console.error(e)
    finally:
        io.close()

def connection_creator():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))
        ack_seq(s)
        print(choices, end='')
        linux_distro = input("=> ").encode()
        if(int(linux_distro) not in [i for i in range(1,4)]):
            console.error(f"are you fu*king blid or what")
            s.close()
            return -1, -1, -1;
        s.send(linux_distro)
        if(send_ack(s)):
            console.info("fetching...")
            container_id = s.recv(1024)
            container_inspect = s.recv(100024).decode()
            container_passwd  = s.recv(1024).strip().decode()
            container_inspect_json = json.loads(container_inspect)
            container_ip = container_inspect_json[0]['NetworkSettings']['Networks']['bridge']['IPAddress']
            return container_id.strip().decode(), container_ip, container_passwd
    except Exception as e:
        raise e

container_id, container_ip, password = connection_creator()
if(container_id == -1 and container_ip == -1 and password == -1): sys.exit(0)
console.success(f"ID: {container_id[:12]}\nIP: {container_ip}\nusername: user\npassword: {password}", showTime=False)
if(input("SSH connection(Y/N):").lower() == 'y'):
    pass
    ssh_shell(container_id, container_ip, password=password)
sys.exit(0)
