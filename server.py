import socketserver as sock
import threading
import random
import sys
import string
import subprocess
from py_console import console
import time


def terminal_size():
    try:
        rows, columns = subprocess.check_output(['stty', 'size']).split()
        return int(columns)
    except subprocess.CalledProcessError as e:
        return int(20)

def clear():
        sys.stdout.write("\033[F")
        sys.stdout.write("\033[K") #clears until EOL

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    BADFAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    BG_ERR_TXT  = '\033[41m' # For critical errors and crashes
    BG_HEAD_TXT = '\033[100m'
    BG_ENDL_TXT = '\033[46m'
    BG_CRIT_TXT = '\033[45m'
    BG_HIGH_TXT = '\033[41m'
    BG_MED_TXT  = '\033[43m'
    BG_LOW_TXT  = '\033[44m'
    BG_INFO_TXT = '\033[42m'

    BG_SCAN_TXT_START = '\x1b[6;30;42m'
    BG_SCAN_TXT_END   = '\x1b[0m'

# Initiliazing the idle loader/spinner class
class Spinner:
    busy = False
    delay = 0.005 # 0.05
    '''
    inspired from the repo: https://github.com/skavngr/rapidscan 
    '''
    @staticmethod
    def spinning_cursor():
        while 1:
            #for cursor in '|/-\\/': yield cursor #←↑↓→
            #for cursor in '←↑↓→': yield cursor
            #for cursor in '....scanning...please..wait....': yield cursor
            for cursor in ' ': yield cursor
    def __init__(self, delay=None):
        self.spinner_generator = self.spinning_cursor()
        if delay and float(delay): self.delay = delay
        self.disabled = False

    def spinner_task(self):
        inc = 0
        try:
            while self.busy:
                if not self.disabled:
                    x = bcolors.BG_SCAN_TXT_START+next(self.spinner_generator)+bcolors.BG_SCAN_TXT_END
                    inc = inc + 1
                    print(x,end='')
                    if inc>random.uniform(0,terminal_size()): #30 init
                        print(end="\r")
                        bcolors.BG_SCAN_TXT_START = '\x1b[6;30;'+str(round(random.uniform(40,47)))+'m'
                        inc = 0
                    sys.stdout.flush()
                time.sleep(self.delay)
                if not self.disabled:
                    sys.stdout.flush()

        except (KeyboardInterrupt, SystemExit):
            print("\n\t"+ bcolors.BG_ERR_TXT+"RapidScan received a series of Ctrl+C hits. Quitting..." +bcolors.ENDC)
            sys.exit(1)

    def start(self):
        self.busy = True
        try:
            threading.Thread(target=self.spinner_task).start()
        except Exception as e:
            print("\n")

    def stop(self):
        try:
            self.busy = False
            time.sleep(self.delay)
        except (KeyboardInterrupt, SystemExit):
            print("\n\t"+ bcolors.BG_ERR_TXT+"RapidScan received a series of Ctrl+C hits. Quitting..." +bcolors.ENDC)
            sys.exit(1)

class Service(sock.BaseRequestHandler):
    allow_resuse_address = True

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
            clear()
            console.info(f"Changing password for user@{container_id[:8]}")
            new_passwd = ''.join([random.choice(string.ascii_letters+string.digits) for i in range(pass_len)])
            command = ["echo", "-e", f"{new_passwd}\n{new_passwd}"]
            io = subprocess.check_output(command)
            change_passwd_command = ["docker", "exec", "-i", container_id, "passwd", user]
            subprocess.check_output(change_passwd_command, input=io)
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
            io = subprocess.check_output(command)
            # console.log(io)
        except Exception as e:
            console.error(e)

    def box_request(self, networkHost=True, storage="500m", verbose=False):
        '''
        Allocates a container for a limited time with a limited storage to the client
        sends `container_id`, `container_passwd`, `container_ip`
        three options are available: Ubuntu, RedHat, Kalirolling
        '''

        spinner = Spinner()
        option = None
        spinner.start()
        try:
            option = int(self.recv(1024))
        except Exception as e:
            console.error("Invalid Box\nError: ")
            console.log(e ,showTime=False)

        if(option == 1):
            clear()
            console.info(f"option: {option}")
            #For Ubuntu Container
            image_name = "ubuntu_ssh"

            try:
                command = ["docker", "container", "create", "-m", storage, "-i", "-t", image_name, "/bin/sh"]
                if(networkHost):
                    command.insert(3, "--network")
                    command.insert(4, "bridge")
                container_io = subprocess.check_output(command)
                container_id = container_io.strip().decode()
                self.send(container_id)
                console.info(f"Starting container {container_id}...")
                start_container_command = ["docker", "container", "start", container_id]
                subprocess.check_output(start_container_command)
                console.success("container started successfully")
                container_inspect_command = ["docker", "inspect", container_id]
                container_inspect = subprocess.check_output(container_inspect_command)
                container_inspect_result = container_inspect.strip().decode()
                self.send(container_inspect_result)
                clear()
                spinner.stop()
                passwd = self.container_password_change(container_id)
                clear()
                console.success(f"Password: {passwd}")
                self.send(passwd)
                console.info("served successfully, socket closed")
                return container_id
            except Exception as e:
                console.warn("Couldn't close the socket!")
                console.error(e)
                return 0

        elif(option == 2):
            clear()
            #For RedHat Container
            console.info(f"option: {option}")
            image_name = "redhat_ssh"
            try:
                command = ["docker", "container", "create", "-m", storage, "-i", "-t", image_name, "/bin/sh"]
                if(networkHost):
                    command.insert(3, "--network")
                    command.insert(4, "bridge")
                container_io = subprocess.check_output(command)
                container_id = container_io.strip().decode()
                self.send(container_id)
                clear()
                spinner.stop()
                console.info(f"Starting container {container_id}...")
                start_container_command = ["docker", "container", "start", container_id]
                subprocess.check_output(start_container_command)
                console.success("container started successfully")
                container_inspect_command = ["docker", "inspect", container_id]
                container_inspect = subprocess.check_output(container_inspect_command)
                container_inspect_result = container_inspect.strip().decode()
                self.send(container_inspect_result)
                clear()
                spinner.stop()
                passwd = self.container_password_change(container_id)
                console.success(f"Password: {passwd}")
                self.send(passwd)
                console.info("served successfully, socket closed")
                return container_id
            except Exception as e:
                console.warn("Couldn't close the socket!")
                console.error(e)
                return 0

        elif(option == 3):
            #For Kali Container
            clear()
            console.info(f"option: {option}")
            image_name = "kali_ssh"
            try:
                command = ["docker", "container", "create", "-m", storage, "-i", "-t", image_name, "/bin/sh"]
                if(networkHost):
                    command.insert(3, "--network")
                    command.insert(4, "bridge")
                container_io = subprocess.check_output(command)
                container_id = container_io.strip().decode()
                self.send(container_id)
                clear()
                spinner.stop()
                console.info(f"Starting container {container_id}...")
                start_container_command = ["docker", "container", "start", container_id]
                subprocess.check_output(start_container_command)
                console.success("container started successfully")
                container_inspect_command = ["docker", "inspect", container_id]
                container_inspect = subprocess.check_output(container_inspect_command)
                container_inspect_result = container_inspect.strip().decode()
                self.send(container_inspect_result)
                clear()
                spinner.stop()
                passwd = self.container_password_change(container_id)
                console.success(f"Password: {passwd}")
                self.send(passwd)
                console.info("served successfully, socket closed")
                return container_id
            except Exception as e:
                console.warn("Couldn't close the socket!")
                console.error(e)
                return 0

        else:
            return -1

    def handle(self):
        container_id = self.box_request()        
        self.container_ssh_start(container_id)
        self.container_rm(container_id, timeout=5) # timeout in seconds
        
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
