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

def GetRSNData(index):
    cipher_suites = [
                    'Group Cipher Suite',
                    'WEP-140',
                    'TKIP',
                    'OCB',
                    'CCMP-128',
                    'WEP-104',
                    'BIP-CMAC-128',
                    'Unkown',
                    'GCMP-128',
                    'GCMP-256',
                    'CCMP-256',
                    'BIP-GMAC-128',
                    'BIP-GMAC-256',
                    'BIP-CMAC-256'
                    ]
    return cipher_suites[index]

def GetAKMData(index):
    akm_suites    = [
                        'Reserved',
                        '802.1X',
                        'PSK',
                        'FT-802.1X',
                        'FT-PSK',
                        'WPA-SHA256',
                        'PSK-SHA256',
                        'TDLS',
                        'SAE',
                        'FT-SAE',
                        'AP-PEER-KEY',
                        'WPA-SHA256-SUITE-B',
                        'WPA-SHA384-SUITE-B',
                        'FT-802.1X-SHA384',
                        'FILS-SHA256',
                        'FILS-SHA384',
                        'FT-FILS-SHA256',
                        'FT-FILS-SHA384',
                        'OWE'
                    ]
    return akm_suites[index]

def GetWPVariant(crypto):
    wp_list = []
    for entry in crypto.keys():
        print(entry)
        wp_list.append(crypto[entry])
    return wp_list

def Parser(pkt):
    #
    try:
        #
        time.sleep(1)
        #
        if(pkt.haslayer(Dot11)):
            #
            if(pkt.haslayer(RSNCipherSuite)):
                cipher = pkt.getlayer(RSNCipherSuite)
                cipher_index = cipher.fields['cipher']
                cipher_eq    = GetRSNData(cipher_index)
                print("Cipher Suite: ",cipher_eq)
            #
            if(pkt.haslayer(AKMSuite)):
                akm_raw = pkt.getlayer(AKMSuite)
                akm_index = akm_raw.fields['suite']
                akm = GetAKMData(akm_index)
                print("AKM: ",akm)
            #
            if(pkt.type== 0 and pkt.subtype == 8):
                #
                stats = pkt[Dot11Beacon].network_stats()
                #
                channel = stats['channel'] ; print('Channel',channel)
                #
                wireless_protection_variant = list(stats['crypto'])
                #
                print(wireless_protection_variant)
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
    # interfaces = get_windows_if_list()
    # #
    # print("[*] Interfaces [*]")
    # #
    # print("------------------")
    # #
    # for i in range(0,len(interfaces)):
    #         #
    #         print( i,")\t",interfaces[i]['name'])
    #         #
    # index = int(input("[+] Enter the interface index-> "))
    # #
    # interface = interfaces[index]['name']
    # #    
    # print("[*] Sniffing traffic on: %s ..." % interface)
    #
    sniff(filter="",store=False,iface=r'%s'%'Wi-Fi 2',prn=Parser,monitor=True)

if(__name__ == '__main__'):
    #
    main()
