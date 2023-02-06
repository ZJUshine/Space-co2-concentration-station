from socket import socket
import sys
import re
import pynmea2
import serial
import chardet
import time
import math
import json
 
global Latitude
global Longitude
global line
global line1
global ser2
 
x_pi = 3.14159265358979324 * 3000.0 / 180.0
pi = 3.1415926535897932384626  # π
a = 6378245.0  # Semi-major axis
ee = 0.00669342162296594323  # Eccentricity squared
 
def _transformlng(longitude, latitude):
    ret = 300.0 + longitude + 2.0 * latitude + 0.1 * longitude * longitude + \
          0.1 * longitude * latitude + 0.1 * math.sqrt(math.fabs(longitude))
    ret += (20.0 * math.sin(6.0 * longitude * pi) + 20.0 *
            math.sin(2.0 * longitude * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(longitude * pi) + 40.0 *
            math.sin(longitude / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(longitude / 12.0 * pi) + 300.0 *
            math.sin(longitude / 30.0 * pi)) * 2.0 / 3.0
    return ret
 
def _transformlat(longitude, latitude):
    ret = -100.0 + 2.0 * longitude + 3.0 * latitude + 0.2 * latitude * latitude + \
          0.1 * longitude * latitude + 0.2 * math.sqrt(math.fabs(longitude))
    ret += (20.0 * math.sin(6.0 * longitude * pi) + 20.0 *
            math.sin(2.0 * longitude * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(latitude * pi) + 40.0 *
            math.sin(latitude / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(latitude / 12.0 * pi) + 320 *
            math.sin(latitude * pi / 30.0)) * 2.0 / 3.0
    return ret
 
def setup():
    # global response
    ser2 = serial.Serial("/dev/ttyUSB0",115200)
    print("ttyUSB0 Open!!!")
    ser2.write('AT+CGPS=1\r'.encode())
    print("AT+CGPS=1")
    ser2.close()
    print("ttyUSB0 Close!!!")
 
def loop():
    global ser1
    ser1 = serial.Serial("/dev/ttyUSB0",115200)
    print("ttyUSB0 Open!!!")
    while True:
        line = str(ser1.readline(),encoding='utf-8')
        if line.startswith("$GPRMC"):
            global Longitude
            global Latitude
            rmc = pynmea2.parse(line)
            if re.match("^\d+?\.\d+?$", rmc.lat)is not None:
                print(rmc)
                latitude = rmc.latitude
                longitude= rmc.longitude
                
# ''' SIM820X uses the gcj_02 coordinate system, no coordinate conversion is required
                dlat = _transformlat(longitude - 105.0, latitude - 35.0)
                dlng = _transformlng(longitude - 105.0, latitude - 35.0)
                radlat = latitude / 180.0 * pi
                magic = math.sin(radlat)
                magic = 1 - ee * magic * magic
                sqrtmagic = math.sqrt(magic)
                dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
                dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
                mglat = latitude + dlat
                mglng = longitude + dlng
# '''Please comment out the conversion part
 
                print ("longitude,latitude")#longitude,latitude
                print (""+str(mglng)+","+str(mglat)+"")#经度,纬度
                time.sleep(2)
def destroy():
    ser1.close()
    print("ttyUSB0 Close!!!")
    ser2 = serial.Serial("/dev/ttyUSB0",115200)
    print("ttyUSB0 Open!!!")
    ser1.close()
    print("ttyUSB0 Close!!!")
    ser2.close()
    print("ttyUSB0 Close!!!")
 
 
try:
    setup()
    loop()
except KeyboardInterrupt:
    destroy()