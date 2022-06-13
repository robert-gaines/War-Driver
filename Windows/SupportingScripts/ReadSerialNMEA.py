#!/usr/bin/env python3

import pynmea2
import serial

def GetGeoFix(port,rate):
    gps_fix = {}
    try:
        serial_instance = serial.Serial()
        serial_instance.baudrate = rate
        serial_instance.port = port
        serial_instance.open()
        if(serial_instance.is_open):
            print("[*] Established serial connection")
        fix_data = serial_instance.readline().decode('ascii',errors='replace')
        fix_data = fix_data.strip()
        if('GP' in fix_data):
            parsed_fix = pynmea2.parse(fix_data)
            latitude   = parsed_fix.latitude
            latitude   = round(latitude,4)
            longitude  = parsed_fix.longitude
            longitude  = round(longitude,4)
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
        else:
            return 'None'
        serial_instance.close()
    except Exception as e:
        print("[!] Error: %s " % e)
        return 'None'
    
    

def main():
    #
    port = 'COM6'
    #
    rate = 4800
    #
    while(True):
        var = GetGeoFix(port,rate)
        print(var)

if(__name__ == '__main__'):
    main()
