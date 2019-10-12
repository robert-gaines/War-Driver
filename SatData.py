#!/usr/bin/env python3

import gps
import sys

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
