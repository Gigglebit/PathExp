#!/bin/bash
#echo "start monitor experiment"
#sudo sysctl -w net.ipv4.tcp_congestion_control=reno
python diamond.py --btn 1 \
		--sim 1 \
		--intf1 eth0 \
		--intf2 eth1 \

echo "cleaning up..."
killall -9 iperf ping
mn -c > /dev/null 2>&1
echo "end"
