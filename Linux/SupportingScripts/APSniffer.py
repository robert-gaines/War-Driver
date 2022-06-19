#!/usr/bin/env python3

from scapy.arch.windows import get_windows_if_list
from scapy.all import *
import time

access_points = []

def AddBuffer(ap):
    #
    if(len(ap) < 25):
        #
        while(len(ap) < 25):
            #
            ap = ap+' '
            #
        return ap

def Parser(pkt):
    #
    try:
        #
        time.sleep(1)
        #
        if(pkt.haslayer(Dot11)):
            #
            pkt.show()
            #
            if(pkt.type== 0 and pkt.subtype == 8):
                #
                if(pkt.addr2 not in access_points):
                    #
                    access_points.append(pkt.addr2)
                    #
                    essid = str(pkt.info,'utf-8')
                    #
                    essid = AddBuffer(essid)
                    #
                    print(essid,pkt.addr2)
                    #
    except:
        pass

def main():
    #
    conf.verb = 0
    #
    interfaces = get_windows_if_list()
    #
    print("[*] Interfaces [*]")
    #
    print("------------------")
    #
    for i in range(0,len(interfaces)):
            #
            print( i,")\t",interfaces[i]['name'])
            #
    index = int(input("[+] Enter the interface index-> "))
    #
    interface = interfaces[index]['name']
    #    
    print("[*] Sniffing traffic on: %s ..." % interface)
    #
    sniff(filter="",store=False,iface=r'%s'%interface,prn=Parser,monitor=True)

if(__name__ == '__main__'):
    #
    main()
