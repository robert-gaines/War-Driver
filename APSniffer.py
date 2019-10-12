#!/usr/bin/env python3

from scapy.all import *

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
    if(pkt.haslayer(Dot11)):
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

def main():
    #
    sniff(iface="wlan0mon",prn=Parser)

if(__name__ == '__main__'):
    #
    main()
