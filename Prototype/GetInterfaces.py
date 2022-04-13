#!/usr/bin/env python3

from scapy.arch.windows import get_windows_if_list

def GetInterfaces():
    interfaces = get_windows_if_list()
    for i in interfaces:
        print(i['name'])

GetInterfaces()