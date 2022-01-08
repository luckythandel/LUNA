#!/bin/env bash

# Server for debian/ubuntu based Linux desktop enviroment (having apt as package manager)


setup()
{
    echo -e "\e[95m@Luckythandel\e[0m";
    echo -e "\e[34mServer Setup\e[0m";
    echo -e "[\e[93m~\e[0m] Installing openvpn & docker";
    apt install docker.io openvpn -y
    # Build Ubuntu Image
    echo "[+]Building Docker image";
    docker build ubuntu/Dockerfile -t "ubuntu_ssh"; 
    # Setup a VPN Server
    exit 0;
    warning="\e[32mIf the server and clients are in the same Local Network, you won't require to setup a VPN server on your system.
    want to proceed further\e[0m(y/n): ";
    echo -e $warning;
    read i;
    while (true);
    do
        if [ $i -eq "y" ];
        then
            echo "OpenVPN Server setup Still in development";
            #curl https://raw.githubusercontent.com/angristan/openvpn-install/master/openvpn-install.sh -o /tmp/openvpn-install.sh
            #chmod +x /tmp/openvpn-install.sh
            #bash /tmp/openvpn-install.sh
        elif [ $i -eq "n" ];
        then
            echo -e "\n\e[31mT\e[0m\e[33mA\e[0m\e[32mT\e[0m\e[34mA\e[0m\e[35m!\e[0m\n";
            break
        else
            echo -e "[\e[41m!\e[0m] Wrong Input";
        fi
        done
}

echo -e "[\e[093m~\e[0m] Python version 3 is required to setup this on your local machine";
echo -e "\e[93m\e[0mChecking...";

if [ -f "/usr/bin/python3" ] && [ `echo `python3 -V` | cut -c 8` -eq "3" ];
then
        echo "Python3 already exists\!";

elif [ -f "/usr/bin/python" ] && [ `echo `python -V` | cut -c 8` -eq "3" ];
then
    echo "Python3 already exists\!";
else
    echo "[\e[93m+\e0m] installing python3 ...";
    apt install python3 -y
    setup();
    echo "[\e[92m+\e[0m] Python3 installed successfully";
fi



