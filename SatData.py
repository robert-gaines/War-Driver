#!/usr/bin/env python3

import matplotlib.pyplot as plt 
import pandas as pd 
import numpy as np 
import gps
import sys

def main():
    #
    BoundaryBox = ((117.0460,116.9426,46.7071,46.7493))
    #
    city = plt.imread("C:\\Users\\robert.gaines\\Desktop\\WarDriver\\moscow.png")
    #
    figure,axis = plt.subplots(figsize=(8,7))
    #
    axis.scatter(dataSet.longitude,dataSet.latitude,zorder=1,alpha=.95,c='r',s=10)
    #
    axis.set_title("Wireless AP's")
    #
    axis.set_xlim(BoundaryBox[0],BoundaryBox[1])
    #
    axis.set_ylim(BoundaryBox[2],BoundaryBox[3])
    #
    axis.imshow(city,zorder=0,extent=BoundaryBox,aspect='equal')
    #
    plt.show()

def main():
    #
    session = gps.gps("localhost", "2947")
    #
    session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
    #
    while True:
        #
        try:
            report = session.next()
            #
            if(report['class'] == 'TPV'):
                #
                try:
                    zuluTime  = report.time
                    latitude  = report.lat
                    longitude = report.lon
                    elevation = report.alt
                    speed     = report.speed
                    #
                    print("""
Time: %s | Latitude: %s | Longitude: %s | Elevation: %s | Velocity: %s
                    """ % (zuluTime,latitude,longitude,elevation,speed))
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
            print("[!] Session terminated [!]")

if(__name__ == '__main__'):
    #
    main()
