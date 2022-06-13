
import folium

coordinates = [
                    ["BoundlessInformant","bc:a5:11:70:44:c7","WPA2/PSK","CCMP-128,PSK","11","N","47.654910","W","-117.1911",629.8,"M",1],
                    ["Unknown","d6:89:ab:f1:c3:14","WPA/802.1X,WPA2/802.1X","CCMP-128,802.1X","11","N","47.404912","W","-117.1911",630.2,"M",1]
              ]

def GetMapBoundaries(coordinates):
    min_lat = 0
    min_lon = 0
    for entry in coordinates:
        latitude  = float(entry[6])
        longitude = float(entry[8])
        min_lat   = latitude
        min_lon   = longitude
        if(latitude < min_lat):
            min_lat = latitude
        if(longitude < min_lon):
            min_lon = longitude
    min_lat = round(min_lat,2)
    min_lon = round(min_lon,2)
    return [min_lat,min_lon]

def PlotAPCoordinates(coordinates):
    map_limit = GetMapBoundaries(coordinates)
    m = folium.Map(location=map_limit)
    for entry in coordinates:
        essid     = entry[0]
        bssid     = entry[1]
        cipher    = entry[2]
        akm       = entry[3] 
        channel   = entry[4]
        latitude  = entry[6]
        longitude = entry[8]
        altitude  = entry[9]
        alt_unit  = entry[10]
        fix_qual  = entry[11]
        if_val    = "ESSID:         %s <br>" % essid
        if_val += "BSSID:           %s <br>" % bssid
        if_val += "CIPHER:          %s <br>" % cipher
        if_val += "AKM:             %s <br>" % akm 
        if_val += "CHANNEL:         %s <br>" % channel
        if_val += "LATITUDE:        %s <br>" % latitude
        if_val += "LONGITUDE:       %s <br>" % longitude
        if_val += "ALTITUDE:        %i <br>" % altitude
        if_val += "ALTITUDE UNIT:   %s <br>" % alt_unit
        if_val += "GPS FIX QUALITY: %i <br>" % fix_qual 
        iframe = folium.IFrame(if_val)
        popup  = folium.Popup(iframe,min_width=300,max_width=300)
        folium.Marker(location=[float(latitude),float(longitude)],popup=popup,icon=folium.Icon(prefix="fa",icon="wifi",color="darkred")).add_to(m)
    m.save("map.html")
    

PlotAPCoordinates(coordinates)
