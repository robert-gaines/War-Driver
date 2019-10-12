#!/usr/bin/env python3

from datetime import datetime
from scapy.all import *
import subprocess
import time
import gps
import sys

n = datetime.now()
t = n.strftime("%m:%d:%Y - %H:%M:%S")
ts = n.strftime("%m_%d_%Y_%H_%M_%S")
log_name = "wardriver_"+ts+'.log'
log_file = open(log_name,'w')

access_points = []

def AddBuffer(ap,value):
    #
    if(len(ap) < value):
        #
        while(len(ap) < value):
            #
            ap = ap+' '
            #
        return ap
        #
    else:
        #
        return ap

def Parser(pkt):
    #
    fix = GPSData()
    #
    try:
        time      = fix[0]
        latitude  = fix[1]
        longitude = fix[2]
        elevation = fix[3]
    except:
        time      = 'None'
        latitude  = 'None'
        longitude = 'None'
        elevation = 'None'
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
                essid = AddBuffer(essid,24) ; latitude = AddBuffer(str(latitude),12); longitude = AddBuffer(str(longitude),14)
                #
                log_str = str(str(time)+'|'+essid+'->'+pkt.addr2+'\t'+"LAT:"+str(latitude)+' '+'LON:'+str(longitude)+' '+'E:'+str(elevation)+'\n')
                #
                log_file.write(log_str)
                #
                print(time,'|',essid,'->',pkt.addr2,'\t',"LAT:",latitude,'','LON:',longitude,'E:',elevation)

def GPSData():
    #
    session = gps.gps("localhost", "2947")
    #
    session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
    #
    fix =[]
    #
    while True:
        #
        try:
            report = session.next()
            #
            if(report['class'] == 'TPV'):
                #
                try:
                    zuluTime  = report.time ; fix.append(zuluTime)
                    latitude  = report.lat  ; fix.append(latitude)
                    longitude = report.lon  ; fix.append(longitude)
                    elevation = report.alt  ; fix.append(elevation)
                    #
                    return fix
                    #
                except:
                    #
                    pass
                    #
        except KeyError:
            #
            pass
            #
        except KeyboardInterrupt:
            #
            sys.exit(0)
            #
        except StopIteration:
            #
            session = None
            #
            sys.exit(1)

def main():
    #
    print("<<< WarDriver >>>")
    #
    print("""
********************************************
Please ensure you have a NIC in monitor mode
and a properly configured antenna with gpsd.
********************************************
    """)
    #
    time.sleep(1)
    #
    iface = input("[+] Enter the network interface-> ")
    #
    print("[*] Selected: %s " % iface)
    #
    time.sleep(1)
    #
    print("[*] Starting... ")
    #
    time.sleep(3)
    #
    subprocess.call('clear',shell=True)
    #
    try:
        #
        sniff(iface=iface,prn=Parser)
        #
    except Exception as e:
        #
        print(str(e))
        #
        print("[!] Exception, departing [!]")
        #
        sys.exit(1)
        #
    finally:
        #
        log_file.close()

if(__name__ == '__main__'):
    #
    main()
