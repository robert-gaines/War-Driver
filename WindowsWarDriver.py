from scapy.arch.windows import get_windows_if_list
from scapy.all import *
import pynmea2
import serial
import time
import sys
import csv
import os

access_points = []
bssid_list    = []

# For the serial connection
# to the GPS Antenna

port = 'COM4'
rate = 4800

n = datetime.now()
t = n.strftime("%m:%d:%Y - %H:%M:%S")
ts = n.strftime("%m_%d_%Y_%H_%M_%S")
log_name = "wardriver_"+ts+'.csv'
log_file = open(log_name,'w')

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
    try:
        if(pkt.haslayer(Dot11)):
            if(pkt.type== 0 and pkt.subtype == 8):
                essid = str(pkt.info,'utf-8')
                essid = AddBuffer(essid,24)
                gps_fix = GetGeoFix(port,rate)
                if(gps_fix != None and pkt.addr2 not in bssid_list):
                    bssid_list.append(pkt.addr2)
                    access_points.append([essid,pkt.addr2,gps_fix])
    except Exception as e:
        print("Exception",e)
        pass
    finally:
        DisplayAccessPoints(access_points)

def DisplayAccessPoints(ap_list):
    latitude_dir = ''
    latitude     = ''
    lon_dir      = ''
    longitude    = ''
    altitude     = ''
    alt_unit     = ''
    gps_quality  = ''
    #
    for element in ap_list:
        essid = element[0]
        bssid = element[1]
        latitude_dir = element[2]['lat_direction']
        latitude     = element[2]['latitude']
        lon_dir      = element[2]['lon_direction']
        longitude    = element[2]['longitude']
        altitude     = element[2]['height']
        alt_unit     = element[2]['height_unit']
        gps_quality  = element[2]['quality']
        print(essid,bssid,latitude_dir,latitude,lon_dir,longitude,altitude,alt_unit,gps_quality)
    time.sleep(1)
    os.system('cls')

def GetGeoFix(port,rate):
    gps_fix = {}
    try:
        serial_instance = serial.Serial()
        serial_instance.baudrate = rate
        serial_instance.port = port
        serial_instance.open()
        '''
        if(serial_instance.is_open):
            print("[*] Established serial connection")
        '''
        fix_data = serial_instance.readline().decode('ascii',errors='replace')
        fix_data = fix_data.strip()
        if('GP' in fix_data):
            parsed_fix = pynmea2.parse(fix_data)
            latitude   = parsed_fix.latitude
            latitude   = round(latitude,2)
            longitude  = parsed_fix.longitude
            longitude  = round(longitude,2)
            lat_dir    = parsed_fix.lat_dir
            lon_dir    = parsed_fix.lon_dir
            altitude   = parsed_fix.altitude
            alt_unit   = parsed_fix.altitude_units
            quality    = parsed_fix.gps_qual ; print(quality)
            #
            gps_fix['latitude']      = latitude
            gps_fix['longitude']     = longitude
            gps_fix['lat_direction'] = lat_dir
            gps_fix['lon_direction'] = lon_dir
            gps_fix['height']        = altitude
            gps_fix['height_unit']   = alt_unit
            gps_fix['quality']       = quality
            #
            return gps_fix
            #
            serial_instance.close()
    except Exception as e:
        print("[!] Error: %s " % e)
        return 'None'

def main():
    #
    print("<<< Windows War Driver >>>")
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
    #
    return

if(__name__ == '__main__'):
    main()
