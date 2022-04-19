#!/usr/bin/env python3

import serial.tools.list_ports

def ListPorts():
    ports = serial.tools.list_ports.comports()
    for p in ports:
        print(p)

ListPorts()

