import socketserver as sock
import threading 
import random
import sys
import string
import subprocess
from py_console import console
import time


class Service(sock.BaseRequestHandler):
    allow_resuse_address = True

    def seq_ack(self):
        seq = str(random.randint(8000, 9000))
        self.send(seq)
        ack = int(self.recv(1024))
        if(int(seq)+1 == ack):
            return True
        return False

    def ack_seq(self):
        ack = int(self.recv(1024))
        seq = ack + 1
        self.send(str(seq))
        return
    
    def container_rm(self, container_id, timeout):
        '''
        container may take space and other resources in the system
        causes system low performency issues
        remove the container using `container_id` and `timeout` arguments
        '''
        time.sleep(timeout)
        console.warn(f"Terminating Container {container_id[:8]}")
        command = ["docker", "kill", container_id]
        try:
            subprocess.run(command)
            command = ["docker", "rm", container_id]
            subprocess.run(command)
            console.success("Container killed successfully")
        except Exception as e:
            console.error(f"Couldn't kill container {container_id[:8]} due to:\n {e}")
            
    def container_password_change(self, container_id, pass_len=12, user="user", root=False):
        '''
        change the password for the docker container 
        default user is `user` with the default password `kingping`
        this fuction generate and change the password for the `user`
        if `root` = True, it changes the root user's password too.
        '''
        try:
            new_passwd = ''.join([random.choice(string.ascii_letters+string.digits) for i in range(pass_len)])
            command = ["echo", "-e", f"{new_passwd}\n{new_passwd}"]
            io = subprocess.run(command, capture_output=True)
            change_passwd_command = ["docker", "exec", "-i", container_id, "passwd", user]
            subprocess.run(change_passwd_command, input=io.stdout)
            if(root):
                command = ["echo", "-e", f"{new_passwd}\n{new_passwd}"]
                io = subprocess.run(command, capture_output=True)
                change_passwd_command = ["docker", "exec", "-i", container_id, "passwd", "root"]
                subprocess.run(change_passwd_command, input=io.stdout)
            return new_passwd
        except Exception as e:
            console.error("""
            Couldn't change the password
            Default password: kingping
            """)
            console.error(e)
            return "kingping"

    def container_ssh_start(self, container_id):
        try:
            command = ["docker", "exec", container_id, "service", "ssh", "restart"]
            io = subprocess.run(command, capture_output=True)
            console.log(io)
        except Exception as e:
            console.error(e)

    def box_request(self, networkHost=True, storage="500m"):
        '''
        Allocates a container for a limited time with a limited storage to the client
        sends `container_id`, `container_passwd`, `container_ip`
        three options are available: Ubuntu, RedHat, Kalirolling
        '''
        if(not self.seq_ack()):
            console.error("Something went wrong")
            return -1
        console.info("handshaking completed")
        option = None
        try:
            option = int(self.recv(1024))
        except Exception as e:
            console.error("Invalid Box\nError: ")
            console.log(e ,showTime=False)

        if(option == 1):
            console.info(f"option: {option}")
            #For Ubuntu Container
            self.ack_seq()
            image_name = "ubuntu_ssh"
            
            try:
                command = ["docker", "container", "create", "-m", storage, "-i", "-t", image_name, "/bin/sh"]
                if(networkHost):
                    command.insert(3, "--network")
                    command.insert(4, "bridge")
                container_io = subprocess.run(command, capture_output=True)
                container_id = container_io.stdout.strip().decode()
                self.send(container_id)
                console.info(f"Starting container {container_id}...")
                start_container_command = ["docker", "container", "start", container_id]
                subprocess.run(start_container_command)
                console.success("container started successfully")
                container_inspect_command = ["docker", "inspect", container_id]
                container_inspect = subprocess.run(container_inspect_command, capture_output=True)
                container_inspect_result = container_inspect.stdout.strip().decode()
                self.send(container_inspect_result)
                passwd = self.container_password_change(container_id)
                console.success(f"Password: {passwd}")
                self.send(passwd)
                console.info("served successfully, socket closed")
                return container_id
            except Exception as e:
                console.warn("Couldn't close the socket!")
                console.error(e)
                return 0

        elif(option == 2):
            #For RedHat
            console.info(f"option: {option}")
            image_name = "hjd48/redhat:latest"
        elif(option == 3):
            #For Kali
            console.info(f"option: {option}")
            image_name = "kalilinux/kali-rolling"
        else:
            return -1

    def handle(self):
        container_id = self.box_request()
        self.container_ssh_start(container_id)
        self.container_rm(container_id, timeout=180) 

    def send(self, string, newline=True):
        try:
            if(newline): string = string+"\n"
            self.request.sendall(string.encode())
            return 0
        except Exception as e:
            console.error(e)
    
    def recv(self, buf):
        try:
            return self.request.recv(buf).decode()
        except Exception as e:
            console.error(e)
            

class ThreadService(sock.ThreadingMixIn, sock.TCPServer, sock.DatagramRequestHandler):
    pass

def main():
    host = "0.0.0.0"
    port = 1337
    s = Service
    server = ThreadService((host, port), s)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    console.info(f"Server Started on port {port}")

    while(True): time.sleep(1)

if(__name__ == "__main__"):
    main()