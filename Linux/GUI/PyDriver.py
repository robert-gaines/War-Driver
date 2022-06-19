#!/usr/bin/env python3

_AUTH_ = 'RWG' # 04142022

from concurrent.futures import thread

try:
    import serial.tools.list_ports
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
    from scapy.all import *
    import pynmea2
    import folium
    import time
    import sys
except Exception as e:
	print("[!] Library Import Exception: %s " % e)
	import sys
	sys.exit(1)

class Worker(QObject):        

    rx_gps_fix            = pyqtSignal(dict)
    located_access_point  = pyqtSignal(list)
    finished              = pyqtSignal()

    def __init__(self,com_port,baud_rate,mon_int):
        super().__init__()
        self.SessionValid      = True
        self.monitor_interface = mon_int
        self.gps_com_port      = com_port
        self.baud_rate         = baud_rate
        self.bssid_list        = []
        self.new_ap_entry      = []
        self.session_list      = []
        self.route_list        = []
        self.log_file          = self.GenerateAPFileName()
        self.log_obj           = open(self.log_file,'w')
        self.log_obj.write('ESSID,BSSID,STANDARD,CIPHER SUITE,AKM,CHANNEL,LATITUDE DIRECTION,LATITUDE,LONGITUDE DIRECTION,LONGITUDE,ALTITUDE,ALTITUDE UNIT,GPS FIX QUALITY\n')
        self.rte_file          = self.GenerateRouteFileName()
        self.rte_obj           = open(self.rte_file,'w')
        self.rte_obj.write('TIME,LATITUDE,LONGITUDE,ELEVATION,ELEVATION UNIT,GPS FIX QUALITY\n')

    def GenerateAPFileName(self):    
        n        = datetime.now()
        t        = n.strftime("%m:%d:%Y - %H:%M:%S")
        ts       = n.strftime("%m_%d_%Y_%H_%M_%S")
        log_file = "Session_"+ts+'.csv'
        return log_file

    def GenerateRouteFileName(self):    
        n        = datetime.now()
        t        = n.strftime("%m:%d:%Y - %H:%M:%S")
        ts       = n.strftime("%m_%d_%Y_%H_%M_%S")
        rte_file = "Route_"+ts+'.csv'
        return rte_file

    def GenerateAPMapFileName(self):    
        n            = datetime.now()
        t           = n.strftime("%m:%d:%Y - %H:%M:%S")
        ts          = n.strftime("%m_%d_%Y_%H_%M_%S")
        ap_map_file = "AP_MAP_"+ts+'.html'
        return ap_map_file

    def GenerateRouteMapFileName(self):    
        n        = datetime.now()
        t        = n.strftime("%m:%d:%Y - %H:%M:%S")
        ts       = n.strftime("%m_%d_%Y_%H_%M_%S")
        log_file = "Route_Map_"+ts+'.html'
        return log_file

    def GenerateCompositeMapFileName(self):    
        n        = datetime.now()
        t        = n.strftime("%m:%d:%Y - %H:%M:%S")
        ts       = n.strftime("%m_%d_%Y_%H_%M_%S")
        log_file = "Composite_Map_"+ts+'.html'
        return log_file

    def GetAPMapBoundaries(self):
        min_lat = 0
        min_lon = 0
        for entry in self.session_list:
            latitude  = float(entry[6])
            longitude = float(entry[7])
            min_lat   = latitude
            min_lon   = longitude
            if(latitude < min_lat):
                min_lat = latitude
            if(longitude < min_lon):
                min_lon = longitude
        min_lat = round(min_lat,2)
        min_lon = round(min_lon,2)
        return [min_lat,min_lon]

    def GetRouteMapBoundaries(self):
        min_lat = 0
        min_lon = 0
        for entry in self.route_list:
            latitude  = float(entry[1])
            longitude = float(entry[2])
            min_lat   = latitude
            min_lon   = longitude
            if(latitude < min_lat):
                min_lat = latitude
            if(longitude < min_lon):
                min_lon = longitude
        min_lat = round(min_lat,2)
        min_lon = round(min_lon,2)
        return [min_lat,min_lon]

    def PlotAPCoordinates(self):
        map_limit = self.GetAPMapBoundaries()
        m = folium.Map(location=map_limit)
        m.add_child(folium.LatLngPopup())
        for entry in self.session_list:
            try:
                essid     = entry[0]
                bssid     = entry[1]
                wp_std    = entry[2]
                cipher    = entry[3]
                akm       = entry[4] 
                channel   = entry[5]
                latitude  = entry[6]
                longitude = entry[7]
                altitude  = entry[8]
                alt_unit  = entry[9]
                fix_qual  = entry[10]
                if_val    = "ESSID:         %s <br>" % essid
                if_val += "BSSID:           %s <br>" % bssid
                if_val += "WPA STANDARD:    %s <br>" % wp_std
                if_val += "CIPHER:          %s <br>" % cipher
                if_val += "AKM:             %s <br>" % akm 
                if_val += "CHANNEL:         %s <br>" % channel
                if_val += "LATITUDE:        %s <br>" % latitude
                if_val += "LONGITUDE:       %s <br>" % longitude
                if_val += "ALTITUDE:        %i <br>" % altitude
                if_val += "ALTITUDE UNIT:   %s <br>" % alt_unit
                if_val += "GPS FIX QUALITY: %s <br>" % fix_qual 
                iframe = folium.IFrame(if_val)
                popup  = folium.Popup(iframe,min_width=300,max_width=300)
                folium.Marker(location=[float(latitude),float(longitude)],popup=popup,icon=folium.Icon(prefix="fa",icon="wifi",color="darkred")).add_to(m)
            except:
                pass
        map_name = self.GenerateAPMapFileName()
        m.save(map_name)

    def PlotRouteCoordinates(self):
        map_limit = self.GetRouteMapBoundaries()
        m = folium.Map(location=map_limit)
        m.add_child(folium.LatLngPopup())
        for entry in self.route_list:
            try:
                timestamp = entry[0]
                latitude  = entry[1]
                longitude = entry[2]
                altitude  = entry[3]
                alt_unit  = entry[4]
                fix_qual  = entry[5]
                if_val    = "PRESENT POSITION INDICATOR <br>" 
                if_val += "TIMESTAMP:       %s <br>" % timestamp
                if_val += "LATITUDE:        %s <br>" % latitude
                if_val += "LONGITUDE:       %s <br>" % longitude
                if_val += "ALTITUDE:        %i <br>" % altitude
                if_val += "ALTITUDE UNIT:   %s <br>" % alt_unit
                if_val += "GPS FIX QUALITY: %s <br>" % fix_qual 
                iframe = folium.IFrame(if_val)
                popup  = folium.Popup(iframe,min_width=300,max_width=300)
                folium.Marker(location=[float(latitude),float(longitude)],popup=popup,icon=folium.Icon(prefix="fa",icon="globe",color="black")).add_to(m)
            except:
                pass
        map_name = self.GenerateRouteMapFileName()
        m.save(map_name)

    def PlotCompositeData(self):
        map_limit =self.GetRouteMapBoundaries()
        m = folium.Map(location=map_limit)
        m.add_child(folium.LatLngPopup())
        for entry in self.route_list:
            try:
                timestamp = entry[0]
                latitude  = entry[1]
                longitude = entry[2]
                altitude  = entry[3]
                alt_unit  = entry[4]
                fix_qual  = entry[5]
                if_val    = "PRESENT POSITION INDICATOR <br>" 
                if_val += "TIMESTAMP:       %s <br>" % timestamp
                if_val += "LATITUDE:        %s <br>" % latitude
                if_val += "LONGITUDE:       %s <br>" % longitude
                if_val += "ALTITUDE:        %i <br>" % altitude
                if_val += "ALTITUDE UNIT:   %s <br>" % alt_unit
                if_val += "GPS FIX QUALITY: %s <br>" % fix_qual 
                iframe = folium.IFrame(if_val)
                popup  = folium.Popup(iframe,min_width=300,max_width=300)
                folium.Marker(location=[float(latitude),float(longitude)],popup=popup,icon=folium.Icon(prefix="fa",icon="globe",color="black")).add_to(m)
            except:
                pass
        for entry in self.session_list:
            try:
                essid     = entry[0]
                bssid     = entry[1]
                wp_std    = entry[2]
                cipher    = entry[3]
                akm       = entry[4] 
                channel   = entry[5]
                latitude  = entry[6]
                longitude = entry[7]
                altitude  = entry[8]
                alt_unit  = entry[9]
                fix_qual  = entry[10]
                if_val    = "ESSID:         %s <br>" % essid
                if_val += "BSSID:           %s <br>" % bssid
                if_val += "WPA STANDARD:    %s <br>" % wp_std
                if_val += "CIPHER:          %s <br>" % cipher
                if_val += "AKM:             %s <br>" % akm 
                if_val += "CHANNEL:         %s <br>" % channel
                if_val += "LATITUDE:        %s <br>" % latitude
                if_val += "LONGITUDE:       %s <br>" % longitude
                if_val += "ALTITUDE:        %i <br>" % altitude
                if_val += "ALTITUDE UNIT:   %s <br>" % alt_unit
                if_val += "GPS FIX QUALITY: %s <br>" % fix_qual 
                iframe = folium.IFrame(if_val)
                popup  = folium.Popup(iframe,min_width=300,max_width=300)
                folium.Marker(location=[float(latitude),float(longitude)],popup=popup,icon=folium.Icon(prefix="fa",icon="wifi",color="darkred")).add_to(m)
            except:
                pass
        map_name = self.GenerateCompositeMapFileName()
        m.save(map_name)

    def GetRSNData(self,index):
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
        return str(cipher_suites[index])

    def GetAKMData(self,index):
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
        return str(akm_suites[index])

    def Parser(self,pkt):
        wp_standard  = ''
        cipher_suite = 'Unknown'
        channel      = 'Undefined'
        akm          = 'Unknown'
        try:
            if(pkt.haslayer(Dot11)):
                if(pkt.type == 0 and pkt.subtype == 8):
                    stats           = pkt[Dot11Beacon].network_stats()
                    wp_standard_raw = list(stats['crypto'])
                    if(len(wp_standard_raw) > 1):
                        for entry in wp_standard_raw:
                            wp_standard += entry
                            wp_standard += ','
                        wp_standard = wp_standard.rstrip(',')
                    else:
                        wp_standard = wp_standard_raw[0]
                    channel         = str(stats['channel']) 
                    if(pkt.info == b''):
                        essid = 'Unknown'
                    elif(len(pkt.info.hex()) > 48):
                        essid = 'Unknown'
                    else:
                        essid = str(pkt.info,'utf-8')
                    if(pkt.haslayer(RSNCipherSuite)):
                        cipher          = pkt.getlayer(RSNCipherSuite)
                        cipher_index    = cipher.fields['cipher']
                        cipher_suite    = self.GetRSNData(cipher_index)
                        cipher_suite    = str(cipher_suite)
                    if(pkt.haslayer(AKMSuite)):
                        akm_raw   = pkt.getlayer(AKMSuite)
                        akm_index = akm_raw.fields['suite']
                        akm       = self.GetAKMData(akm_index)
                        akm       = str(akm)
                    if(pkt.addr2 not in self.bssid_list):
                        ap_geo_fix = self.GetGeoFix(self.gps_com_port,self.baud_rate)
                        if((essid == '') or ('NULL' in essid )):
                            essid = 'Unknown'
                        latitude   = str(ap_geo_fix['lat_direction'])+' '+str(ap_geo_fix['latitude'])
                        longitude  = str(ap_geo_fix['lon_direction'])+' '+str(ap_geo_fix['longitude'])
                        altitude   = str(ap_geo_fix['height'])+' '+str(ap_geo_fix['height_unit'])
                        fix_qual   = str(ap_geo_fix['quality'])
                        bssid      = pkt.addr2
                        self.bssid_list.append(bssid)
                        self.new_ap_entry = [essid,bssid,wp_standard,cipher_suite,akm,channel,latitude,longitude,altitude,fix_qual]
                        self.session_list.append([essid,bssid,wp_standard,cipher_suite,akm,channel,ap_geo_fix['latitude'],ap_geo_fix['longitude'],ap_geo_fix['height'],ap_geo_fix['height_unit'],fix_qual])
                        log_entry = "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (essid,bssid,wp_standard,cipher_suite,akm,channel,str(ap_geo_fix['lat_direction']),str(ap_geo_fix['latitude']),str(ap_geo_fix['lon_direction']),str(ap_geo_fix['longitude']),str(ap_geo_fix['height']),str(ap_geo_fix['height_unit']),fix_qual)
                        self.log_obj.write(log_entry)
                        self.located_access_point.emit(self.new_ap_entry)
        except:
            pass
        finally:
            return

    def GetGeoFix(self,port,rate):
        gps_fix = {}
        try:
            serial_instance          = serial.Serial()
            serial_instance.baudrate = rate
            serial_instance.port     = port
            serial_instance.open()
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
                quality    = parsed_fix.gps_qual
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
                return None
            serial_instance.close()
        except:
            return None

    def RunSession(self):
        while(self.SessionValid):
            self.current_gps_fix = self.GetGeoFix(self.gps_com_port,self.baud_rate)
            try:
                latitude    = self.current_gps_fix['latitude']
                longitude   = self.current_gps_fix['longitude']
                height      = self.current_gps_fix['height']
                height_unit = self.current_gps_fix['height_unit']
                fix_quality = self.current_gps_fix['quality']
                ts          = time.ctime()
                pos_entry   = str(ts)
                pos_entry   += ','
                pos_entry   += str(latitude)
                pos_entry   += ','
                pos_entry   += str(longitude)
                pos_entry   += ','
                pos_entry   += str(height)
                pos_entry   += ','
                pos_entry   += str(height_unit)
                pos_entry   += ','
                pos_entry   += str(fix_quality)
                pos_entry   += "\n"
                self.rte_obj.write(pos_entry)
                self.route_list.append([ts,latitude,longitude,height,height_unit,fix_quality])
            except Exception as e:
                pass
            sniff(filter="",store=False,count=64,iface=r'%s'%self.monitor_interface,prn=self.Parser,monitor=True)
            if(self.current_gps_fix):
                self.rx_gps_fix.emit(self.current_gps_fix)
            time.sleep(1)
        self.finished.emit()

    def TerminateSession(self):
        self.SessionValid = False
        self.log_obj.close() 
        self.rte_obj.close()

class Window(QWidget):

    terminate_session = pyqtSignal()
    export_ap_data    = pyqtSignal()
    export_rte_data   = pyqtSignal()
    export_composite  = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.identified_access_points = []
        self.bssid_list               = []
        self.UI()

    def UI(self,parent=None):
        #
        super().__init__(parent)
        #
        QMainWindow.__init__(self)
        QTableWidget.__init__(self)
        QWidget.__init__(self)
        QLabel.__init__(self)
        #
        self.setWindowTitle('Python War Driver')
        self.setGeometry(350,200,1600,800)
        #
        self.setStyleSheet("""background-color: #403e3e; 
                              border: 2px black solid ; 
                              color: #0bba11; 
                              font-size: 16px;
                              font-style: bold; 
                              font-family: Arial""")
        #
        self.com_port_label           = QLabel("COM Port for the GPS Antenna")
        self.com_port_combo_box       = QComboBox()
        self.com_ports                = self.ListPorts()
        for port in self.com_ports:
            self.com_port_combo_box.addItem(str(port))
        self.com_port_combo_box.setStyleSheet("background-color: black; border: 2px groove #0bba11; border-radius: 2px; font-style: bold; font-size: 16px; font-family: Arial")
        self.baud_rate_label          = QLabel("Baud Rate for the Serial Connection")
        self.baud_rate                = QComboBox()
        self.baud_rates               = [
                                            '75',
                                            '110',
                                            '134.5',
                                            '150',
                                            '300',
                                            '600',
                                            '1200',
                                            '1800',
                                            '2400',
                                            '4800',
                                            '7200',
                                            '9600',
                                            '14400',
                                            '19200',
                                            '38400',
                                            '56000',
                                            '76800',
                                            '56000',
                                            '57000',
                                            '76800',
                                            '115200',
                                            '230400',
                                            '250000',
                                            '256000'
                                        ]
        for rate in self.baud_rates:
            self.baud_rate.addItem(rate)
        self.baud_rate.setStyleSheet("background-color: black; border: 2px groove #0bba11; border-radius: 2px; font-style: bold; font-size: 16px; font-family: Arial")
        #
        self.mon_int_label            = QLabel("Monitoring Wireless Interface")
        self.mon_int_combo_box        = QComboBox()
        self.net_ifaces               = self.GetInterfaces()
        for interface in self.net_ifaces:
            self.mon_int_combo_box.addItem(interface)
        self.mon_int_combo_box.setStyleSheet("background-color: black; border: 2px groove #0bba11; border-radius: 2px; font-style: bold; font-size: 16px; font-family: Arial")
        #
        self.start_button        = QPushButton("Start Session",self)
        self.stop_button         = QPushButton("Stop Session", self)
        self.conf_button         = QPushButton("Set Parameters",self)
        self.reset_button        = QPushButton("Reset Session", self)
        self.export_route_button = QPushButton("Export Route Map", self)
        self.export_ap_button    = QPushButton("Export Access Point Map", self)
        self.export_cmp_button   = QPushButton("Export Composite Data Map", self)
        self.start_button.setStyleSheet("background-color: black; border: 2px groove #0bba11; border-radius: 10px; font-style: bold; font-size: 16px; font-family: Arial")
        self.stop_button.setStyleSheet("background-color: black; border: 2px groove #0bba11; border-radius: 10px; font-style: bold; font-size: 16px; font-family: Arial")
        self.conf_button.setStyleSheet("background-color: black; border: 2px groove #0bba11; border-radius: 10px; font-style: bold; font-size: 16px; font-family: Arial")
        self.reset_button.setStyleSheet("background-color: black; border: 2px groove #0bba11; border-radius: 10px; font-style: bold; font-size: 16px; font-family: Arial")
        self.export_route_button.setStyleSheet("background-color: black; border: 2px groove #0bba11; border-radius: 10px; font-style: bold; font-size: 16px; font-family: Arial")
        self.export_ap_button.setStyleSheet("background-color: black; border: 2px groove #0bba11; border-radius: 10px; font-style: bold; font-size: 16px; font-family: Arial")
        self.export_cmp_button.setStyleSheet("background-color: black; border: 2px groove #0bba11; border-radius: 10px; font-style: bold; font-size: 16px; font-family: Arial")
        #
        self.current_latitude_label    = QLabel("Current Latitude")
        self.current_latitude          = QLineEdit()
        self.current_latitude.setFixedWidth(500)
        self.current_latitude.setStyleSheet("background-color: black; border:2px groove #0bba11; border-radius: 10px; font-style: bold; font-size: 16px; font-family: Arial") 
        self.current_longitude_label   = QLabel("Current Longitude")
        self.current_longitude         = QLineEdit()
        self.current_longitude.setFixedWidth(500)
        self.current_longitude.setStyleSheet("background-color: black; border:2px groove #0bba11; border-radius: 10px; font-style: bold; font-size: 16px; font-family: Arial") 
        self.current_elevation_label   = QLabel("Elevation")
        self.current_elevation         = QLineEdit()
        self.current_elevation.setFixedWidth(500)
        self.current_elevation.setStyleSheet("background-color: black; border:2px groove #0bba11; border-radius: 10px; font-style: bold; font-size: 16px; font-family: Arial")
        self.current_fix_quality_label = QLabel("GPS Fix Quality")
        self.current_fix_quality       = QLineEdit()
        self.current_fix_quality.setFixedWidth(500)
        self.current_fix_quality.setStyleSheet("background-color: black; border:2px groove #0bba11; border-radius: 10px; font-style: bold; font-size: 16px; font-family: Arial")
        #
        self.tableWidgetLabel = QLabel("Identified Wireless Access Points")
        self.tableWidget      = QTableWidget()
        self.tableWidget.setStyleSheet("background-color: black; color: #0bba11; border: 2px groove #218024; border-radius: 2px; font-style: bold; font-size: 16px; font-family: Arial")
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.horizontalHeader().setVisible(False)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget.setColumnCount(10)
        self.tableWidget.setRowCount(1)
        self.tableWidget.setItem(0,0,QTableWidgetItem("ESSID"))
        self.tableWidget.setItem(0,1,QTableWidgetItem("BSSID"))
        self.tableWidget.setItem(0,2,QTableWidgetItem("STANDARD"))
        self.tableWidget.setItem(0,3,QTableWidgetItem("CIPHER SUITE"))
        self.tableWidget.setItem(0,4,QTableWidgetItem("AUTH KEY MGMT"))
        self.tableWidget.setItem(0,5,QTableWidgetItem("CHANNEL"))
        self.tableWidget.setItem(0,6,QTableWidgetItem("LATITUDE"))
        self.tableWidget.setItem(0,7,QTableWidgetItem("LONGITUDE"))
        self.tableWidget.setItem(0,8,QTableWidgetItem("ELEVATION"))
        self.tableWidget.setItem(0,9,QTableWidgetItem("GPS FIX QUALITY"))
        #
        main_layout               = QFormLayout()
        self.com_config_container = QVBoxLayout()
        self.int_config_container = QVBoxLayout()
        self.control_container    = QHBoxLayout()
        self.position_container   = QHBoxLayout()
        self.position_ctr_sub     = QHBoxLayout()
        self.status_container     = QHBoxLayout()
        self.display_container    = QVBoxLayout()
        self.export_container     = QHBoxLayout()
        #
        self.com_config_container.addWidget(self.com_port_label)
        self.com_config_container.addWidget(self.com_port_combo_box)
        self.com_config_container.addWidget(self.baud_rate_label)
        self.com_config_container.addWidget(self.baud_rate)
        self.int_config_container.addWidget(self.mon_int_label)
        self.int_config_container.addWidget(self.mon_int_combo_box)
        self.control_container.addWidget(self.conf_button)
        self.control_container.addWidget(self.start_button)
        self.control_container.addWidget(self.reset_button)
        self.control_container.addWidget(self.stop_button)
        self.position_container.addWidget(self.current_latitude_label)
        self.position_container.addWidget(self.current_latitude)
        self.position_container.addWidget(self.current_longitude_label)
        self.position_container.addWidget(self.current_longitude)
        self.position_ctr_sub.addWidget(self.current_elevation_label)
        self.position_ctr_sub.addWidget(self.current_elevation)
        self.position_ctr_sub.addWidget(self.current_fix_quality_label)
        self.position_ctr_sub.addWidget(self.current_fix_quality)
        self.display_container.addWidget(self.tableWidgetLabel)
        self.display_container.addWidget(self.tableWidget)
        self.export_container.addWidget(self.export_route_button)
        self.export_container.addWidget(self.export_ap_button)
        self.export_container.addWidget(self.export_cmp_button)
        main_layout.addRow(self.com_config_container)
        main_layout.addRow(self.int_config_container)
        main_layout.addRow(self.control_container)
        main_layout.addRow(self.position_container)
        main_layout.addRow(self.position_ctr_sub)
        main_layout.addRow(self.status_container)
        main_layout.addRow(self.display_container)
        main_layout.addRow(self.export_container)
        #
        self.conf_button.clicked.connect(self.InitializeSession)
        self.reset_button.clicked.connect(self.ResetSession)
        #
        self.setLayout(main_layout)

    def InitializeSession(self):
        #
        gps_com_port  = self.com_port_combo_box.currentText() 
        gps_com_port  = gps_com_port.split('-')[0] 
        ant_baud_rate = self.baud_rate.currentText()
        ws_mon_int    = self.mon_int_combo_box.currentText()
        #
        self.thread          = QThread(parent=self)
        self.MainWorker      = Worker(gps_com_port,ant_baud_rate,ws_mon_int)
        self.terminate_session.connect(self.MainWorker.TerminateSession)
        self.export_ap_data.connect(self.MainWorker.PlotAPCoordinates)
        self.export_rte_data.connect(self.MainWorker.PlotRouteCoordinates)
        self.export_composite.connect(self.MainWorker.PlotCompositeData)       
        self.MainWorker.moveToThread(self.thread)
        #
        self.MainWorker.rx_gps_fix.connect(lambda: self.SetPresentPosition(self.MainWorker.current_gps_fix))
        self.MainWorker.located_access_point.connect(lambda: self.AddAccessPointTableEntry(self.MainWorker.new_ap_entry))
        #
        self.MainWorker.finished.connect(self.thread.quit) 
        self.MainWorker.finished.connect(self.thread.deleteLater)  
        self.thread.finished.connect(self.thread.deleteLater)  
        #
        self.thread.started.connect(self.MainWorker.RunSession)
        self.thread.finished.connect(self.MainWorker.TerminateSession)
        #
        self.start_button.clicked.connect(self.thread.start)
        self.stop_button.clicked.connect(self.StopSession)
        self.reset_button.clicked.connect(self.ResetSession)
        self.export_ap_button.clicked.connect(self.PlotAccessPoints)
        self.export_route_button.clicked.connect(self.PlotRoutePoints)
        self.export_cmp_button.clicked.connect(self.PlotCompositePoints)

    def SetPresentPosition(self,gps_fix):
        latitude_raw  = str(gps_fix['latitude'])
        lat_direction = str(gps_fix['lat_direction'])
        latitude      = lat_direction+' '+latitude_raw 
        longitude_raw = str(gps_fix['longitude'])
        lon_direction = str(gps_fix['lon_direction'])
        longitude     = lon_direction+' '+longitude_raw
        altitude      = str(gps_fix['height'])
        alt_unit      = str(gps_fix['height_unit'])
        alt_str       = altitude+' '+alt_unit
        fix_quality   =  str(gps_fix['quality'])
        self.current_latitude.setText(latitude) 
        self.current_longitude.setText(longitude)
        self.current_elevation.setText(alt_str)
        self.current_fix_quality.setText(fix_quality)

    def AddAccessPointTableEntry(self,ap_entry):
        essid       = str(ap_entry[0])
        bssid       = str(ap_entry[1])
        wp_standard = str(ap_entry[2])
        cipher_ste  = str(ap_entry[3])
        akm         = str(ap_entry[4])
        channel     = str(ap_entry[5])
        latitude    = str(ap_entry[6])
        longitude   = str(ap_entry[7])
        elevation   = str(ap_entry[8])
        fix_quality = str(ap_entry[9])
        current_row = self.tableWidget.rowCount()
        self.tableWidget.setRowCount(current_row+1)
        col_index   = 0
        cell_value  = QTableWidgetItem(essid)
        cell_value.setForeground(QBrush(QColor('#218024')))
        self.tableWidget.setItem(current_row,col_index,cell_value) 
        col_index   = 1
        cell_value  = QTableWidgetItem(bssid)
        cell_value.setForeground(QBrush(QColor('#218024')))
        self.tableWidget.setItem(current_row,col_index,cell_value)
        col_index   = 2
        cell_value  = QTableWidgetItem(wp_standard)
        cell_value.setForeground(QBrush(QColor('#218024')))
        self.tableWidget.setItem(current_row,col_index,cell_value)
        col_index   = 3
        cell_value  = QTableWidgetItem(cipher_ste)
        cell_value.setForeground(QBrush(QColor('#218024')))
        self.tableWidget.setItem(current_row,col_index,cell_value)
        col_index   = 4
        cell_value  = QTableWidgetItem(akm)
        cell_value.setForeground(QBrush(QColor('#218024')))
        self.tableWidget.setItem(current_row,col_index,cell_value)
        col_index   = 5
        cell_value  = QTableWidgetItem(channel)
        cell_value.setForeground(QBrush(QColor('#218024')))
        self.tableWidget.setItem(current_row,col_index,cell_value)
        col_index   = 6
        cell_value  = QTableWidgetItem(latitude)
        cell_value.setForeground(QBrush(QColor('#218024')))
        self.tableWidget.setItem(current_row,col_index,cell_value)
        col_index   = 7
        cell_value  = QTableWidgetItem(longitude)
        cell_value.setForeground(QBrush(QColor('#218024')))
        self.tableWidget.setItem(current_row,col_index,cell_value)
        col_index   = 8
        cell_value  = QTableWidgetItem(elevation)
        cell_value.setForeground(QBrush(QColor('#218024')))
        self.tableWidget.setItem(current_row,col_index,cell_value)
        col_index   = 9
        cell_value  = QTableWidgetItem(fix_quality)
        cell_value.setForeground(QBrush(QColor('#218024')))
        self.tableWidget.setItem(current_row,col_index,cell_value)
        self.tableWidget.update()
        return

    def PlotAccessPoints(self):
        self.export_ap_data.emit()

    def PlotRoutePoints(self):
        self.export_rte_data.emit()

    def PlotCompositePoints(self):
        self.export_composite.emit()

    def ResetSession(self):
        self.current_latitude.setText('')
        self.current_longitude.setText('')
        self.current_elevation.setText('')
        self.current_fix_quality.setText('')
        for row in range(self.tableWidget.rowCount()-1):
            try:
                self.tableWidget.removeRow(self.tableWidget.rowCount()-1)
                self.tableWidget.update()
            except:
                sys.exit(1)

    def ListPorts(self):
        ports = serial.tools.list_ports.comports()
        return ports

    def GetInterfaces(self):
        interfaces = get_if_list()
        return interfaces

    def StopSession(self):
        #
        self.thread.quit()
        self.terminate_session.emit()

if(__name__ == '__main__'):
    app = QApplication(sys.argv)
    screen = Window()
    screen.show()
    sys.exit(app.exec_())
