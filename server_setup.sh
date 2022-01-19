#!/bin/env bash

# Server for debian/ubuntu based Linux desktop enviroment (having apt as package manager)

array_adapters=();
selected_adapters=();
client_side()
{
    docker_ip="`ip addr show ${selected_adapters[1]} | grep 'inet ' | awk {'print $2'}`";
    docker_netmask="`ip addr show ${selected_adapters[1]} | grep 'inet ' | awk {'print $4'}`";
    in_ip="`ip addr show ${selected_adapters[0]} | grep 'inet ' | awk {'print $2'}`";
    docker_netmask="`ip addr show ${selected_adapters[0]} | grep 'inet ' | awk {'print $4'}`";
    gateway="`ip route | grep ${selected_adapters[1]} | awk {'print $9'}`";
    echo -e "[\e[93m!\e[0m] You will have to route the traffic from client too";
    echo -e "\e[92m[\e[0m Run these following commands according to your system \e[92m]\e[0m";
    echo -e "\e[35mLinux\e[0m\n\$ ip route add $docker_ip via $gateway";
    echo -e "\e[34mWindows\e[0m\n\$ route add ${docker_ip::-3} MASK $docker_netmasak $gateway";
}

adapters()
{
    echo -e "\e[36m===>pick network interfaces<===\e[0m";
    i=0;
    for iface in $(ifconfig | cut -d ' ' -f1| tr ':' '\n' | awk NF)
    do
        echo -n "$i.) ";
        printf "$iface\n";
        array_adapters+=("$iface");
       i=`expr $i + 1`;
    done
}

iptables_config()
{
    in_interface=$1;
    docker_interface=$2;
    echo -e "\e[45m$in_interface\e[0m \e[92m<------------->\e[0m \e[44m$docker_interface\e[0m";
    iptables -A FORWARD -i $in_interface -o $docker_interface -j ACCEPT;
    iptables -A FORWARD -i $docker_interface -o $in_interface -m state --state ESTABLISHED,RELATED -j ACCEPT
    iptables -t nat -A POSTROUTING -o $docker_interface -j MASQUERADE
}

setup()
{
    echo -e "\e[95m@Luckythandel\e[0m";
    echo -e "\e[34mServer Setup\e[0m";
    echo -e "[\e[93m~\e[0m] Installing openvpn & docker";
    apt install runc docker.io openvpn -y
    # Build Ubuntu, Kali, RedHat Image
    echo "[+] Building Docker images";
    docker build ubuntu/ -t "ubuntu_ssh";
    docker build kali/ -t "kali_ssh";
    docker build redhat/ -t "redhat_ssh";
    warning="[\e[33m!\e[0m]server and client testing on a single system is possible without routing ";
    echo -e $warning;
    read -p "Do you want to setup routing(y/n): " -e -i y user;
    if [ $user = 'n' ];
    then
        echo -e "\n\e[31mT\e[0m\e[33mA\e[0m\e[32mT\e[0m\e[34mA\e[0m\e[35m!\e[0m\n";
    elif [ $user = 'y' ];
    then
        echo -e "[\e[93m~\e[0m] Checking ip4 forwarding..."
        ipf=`cat /proc/sys/net/ipv4/ip_forward`;
        if [ $ipf -eq '1' ];
            # when ipforwarding is enabled
        then
            echo -e "[\e[92m~\e[0m] ipv4 forwaring enable already";
            echo -e "[\e[92m~\e[0m] setting up iptable rules";
            adapters
            echo -ne "[\e[93m?\e[0m] interface, which has the the traffic to redirect: ";
            read -e -i 5 in_interface_index;
            echo -ne "[\e[93m?\e[0m] interface, to which the traffic will be routed: ";
            read -e -i 0 docker_interface_index;
            in_interface=${array_adapters[$in_interface_index]};
            docker_interface=${array_adapters[$docker_interface_index]};
            selected_adapters=($in_interface $docker_interface);
            iptables_config $in_interface $docker_interface;
            echo -e "[\e[32m+\e[0m] your system is configured successfully!";
            client_side;
            echo -e "\n\e[31mT\e[0m\e[33mA\e[0m\e[32mT\e[0m\e[34mA\e[0m\e[35m!\e[0m\n";

        else
            echo -e "[\e[91m~\e[0m] ipv4 forwaring is not enabled";
            echo -e "[\e[93m~\e[0m] in order to procceed further, you will have to enable ipv4 forwarding"
            echo -ne "[\e[93m?\e[0m] do you want to continue(y/n): ";
            read -e -i y should_we;
            if [ $should_we != 'y' ];
            then
                echo -e "\n\e[31mT\e[0m\e[33mA\e[0m\e[32mT\e[0m\e[34mA\e[0m\e[35m!\e[0m\n";
                return;
            fi
            echo 1 > /proc/sys/net/ipv4/ip_forward;
            echo -e "[\e[92m~\e[0m] ipv4 forwrding enabled";
            echo -e "[\e[92m~\e[0m] setting up iptable rules";
            adapters
            echo -ne "[\e[93m?\e[0m] interface, which has the the traffic to redirect: ";
            read -e -i 5 in_interface_index;
            echo -ne "[\e[93m?\e[0m] interface, to which the traffic will be routed: ";
            read -e -i 0 docker_interface_index;
            in_interface=${array_adapters[$in_interface_index]};
            docker_interface=${array_adapters[$docker_interface_index]};
            #selected_adapters[0]=in_interface; selected_adapters[1]=docker_interface;
            selected_adapters=($in_interface $docker_interface);
            iptables_config $in_interface $docker_interface;
            echo -e "[\e[32m+\e[0m] your system is configured successfully!";
            client_side;
            echo -e "\e[31mT\e[0m\e[33mA\e[0m\e[32mT\e[0m\e[34mA\e[0m\e[35m!\e[0m";

        fi
    fi
}

echo -e "[\e[93m~\e[0m] Python version 3 is required";
echo -e "[\e[93m~\e[0m] Checking...";

if [ -f "/usr/bin/python3" ] && [ $(echo "`python3 -V`" | cut -c 8) -eq "3" ];
then
        echo 'Python3 already exists!';
        setup
    elif [ -f "/usr/bin/python" ] && [ $(echo "`python -V`" | cut -c 8) -eq "3" ];
then
    echo "Python3 already exists\!";
    setup
else
    echo -e "[\e[93m+\e[0m] installing python3 ...";
    apt install python3 -y
    setup
    echo -e "[\e[92m+\e[0m] Python3 installed successfully";
fi



