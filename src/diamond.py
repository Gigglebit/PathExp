#!/usr/bin/python
import re
import sys
import os
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import irange,dumpNodeConnections
from mininet.log import setLogLevel
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.node import Node,Controller,RemoteController,OVSKernelSwitch
from mininet.cli import CLI
from argparse import ArgumentParser
from nathw import *
parser = ArgumentParser(description = "Pulling Stats Tests")
parser.add_argument('--btn', '-b',
                    dest="btn",
                    action="store",
                    help="Bottleneck link speed",
                    required=True)
parser.add_argument('--sim',
                    dest="sim",
                    type=int,
                    action="store",
                    help="if True, no real interface added",
                    required=True)
parser.add_argument('--intf1',
                    dest="intf1",
                    type=str,
                    action="store",
                    help="Real Interface",
                    required=True)
parser.add_argument('--intf2',
                    dest="intf2",
                    type=str,
                    action="store",
                    help="Real Interface",
                    required=True)
args = parser.parse_args()

class DiamondTopo(Topo):
   "Linear topology of k switches, with one host per switch."

   def __init__(self, k=4, **opts):
       """Init.
           k: number of switches (and hosts)
           hconf: host configuration options
           lconf: link configuration options"""

       super(DiamondTopo, self).__init__(**opts)

       self.k = k

       lastSwitch = None
       for i in irange(1, k):
           host = self.addHost('h%s' % i)
           switch = self.addSwitch('s%s' % i)
           self.addLink( host, switch)
           if lastSwitch:
               self.addLink( switch, lastSwitch, bw = int(args.btn))
           lastSwitch = switch
       self.addLink('s1','s4')

topos = { 'mytopo': ( lambda: DiamondTopo() ) }
def simpleTest():
   "Create and test a simple network"
   topo = DiamondTopo(k=4)
   net = Mininet(topo=topo,link=TCLink,controller=RemoteController)
   if args.sim!=1:
        print "Adding real interfaces" 
   	s1 = net.getNodeByName('s1')
   	s3 = net.getNodeByName('s3')
   	addRealIntf(net,args.intf1,s1)
   	addRealIntf(net,args.intf2,s3)
   	opts = '-D -o UseDNS=no -u0'
   	rootnode=sshd(net, opts=opts)
	h2 = net.getNodeByName('h2')
   	h2.cmd('iperf -s -p 5001 -i 1 > iperf-recv_TCP.txt &')
   	h2.cmd('iperf -s -p 5003 -u -i 1 > iperf-recv_UDP.txt &')
   else:
   	net.start()
   CLI(net)

   os.system('killall -9 iperf' )
   
   if args.sim!=1:
	net.hosts[0].cmd('killall -9 dhcpd')   
	for host in net.hosts:
       		host.cmd('kill %'+ '/usr/sbin/sshd')
   	stopNAT(rootnode)
   net.stop()

if __name__ == '__main__':
   # Tell mininet to print useful information
   setLogLevel('info')
   simpleTest()
