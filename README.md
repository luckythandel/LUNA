![Logo](https://github.com/luckythandel/LUNA/blob/main/assets/cover/Luna.jpg)
#### Your Linux system is not your Linux System anymore 
[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)    
[![forthebadge docker_containers](http://github.com/luckythandel/LUNA/blob/main/assets/badges/docker-containers.svg)](https://www.docker.com/)    
[![GitHub license](https://img.shields.io/github/license/Naereen/StrapDown.js.svg)](https://github.com/Naereen/StrapDown.js/blob/master/LICENSE)

# About the project
SSH Sandboxing over the network using Python3. you can create your own server which provides Docker containers 
to the requests. It won't easily crash with simultaneous requests due to the implementation of multi-threading in sockets.
Tested on Kalirolling. Luna project is made to overcome the problem of providing Linux systems at a place (University Lab) where hosts are using Windows Machines and Time is short to install Linux in each System.
LUNA will work from one system which has Linux installed in it (to fulfil the requirements of docker to run Linux containers over a Linux kernel host only) and will serve other systems.
For now, it is just an ubuntu container, you can spawn, but soon, Redhat & Kali will also be there.

# Features
- Easy to read & customize
- SSH direct connection through (`client.py`)
- Interactive panel for quick results
- Error handling over the network
- container_storage, container_timeout etc can vary
- memory-efficient
- setup is easy (`setup.sh`)

# Installation & Setup
1. clone the repository on the server machine and Client machine
```sh
$ git clone https://github.com/luckythandel/LUNA.git
```
2. setup the server machine
```sh
$ chmod +x ./setup.sh
$ ./setup.sh 
```
3. start the server
```bash
$ python3 server.py
```
4. let the client choose
```bash
$ python3 client.py
```
*Note: default port started by the server is `1337`, you can change it in `server.py` & `client.py` both*


# Comming Soon
- Expansion of networks
- OpenVPN setup automation
- Redhat & kali 
- Ubuntu with more utilities 
- Maybe privileged containers (where you can interact with kernel drives)
