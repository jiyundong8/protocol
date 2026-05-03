#使用Python制造免费ARP(Gratuitous ARP)

from socket import PACKET_BROADCAST
from scapy.all import *

iface = "ens192"

ip = "10.1.1.1"

arp = ARP(
    op=1,
    psrc=ip,
    pdst=ip,
    hwsrc="aa:bb:cc:dd:ee:ff"
)

eth = Ether(
    dst="ff:ff:ff:ff:ff:ff",
    src="aa:bb:cc:dd:ee:ff"
)

packet = eth / arp

sendp(packet,iface=iface,count=5,inter=1)