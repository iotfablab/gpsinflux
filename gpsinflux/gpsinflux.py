#!/usr/bin/env python3
# Python3 Command Line Utility to read from MTK GPS Module (Adafruit) connected
# to serial ports and store GPS relevant information to InfluxDB either via UDP
# or HTTP
# Author: Shantanoo Desai <des@biba.uni-bremen.de>

import sys
import struct
import logging
import json
import time
import datetime
import argparse
import serial
import pynmea2
from .mt3339 import mt3339
from influxdb import InfluxDBClient
from influxdb.client import InfluxDBClientError

# Logger Settings
logger = logging.getLogger("main")
logger.setLevel(logging.ERROR)

handler = logging.FileHandler("/var/log/gpsinflux.log")
handler.setLevel(logging.ERROR)

formatter = logging.Formatter('%(asctime)s-%(name)s-%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

CONF_PATH = '/etc/umg/conf.json'

com = None

client = None

def gps_setup(serialport, baudrate, updaterate):
    try:
        gps = mt3339(serialport)
        gps.set_baudrate(baudrate)
        gps.set_nmea_update_rate(updaterate)
        gps.set_nmea_output(gll = 0, rmc = 3, vtg = 0, gga = 0, gsa = 0, gsv = 0)
    except Exception as e:
        logger.exception('Exception Occured while setting up GPS')
        raise(e)


def send_data(serialport, baudrate, updaterate, db_host, db_port, udp_port):
    logger.info('Setting Up GPS')
    logger.debug('GPS Config: %s %d %d' % (serialport, baudrate, updaterate))
    gps_setup(serialport, baudrate, updaterate)

    global client
    logger.info('UDP Sending selected')
    try:
        client = InfluxDBClient(host=db_host, port=db_port, use_udp=True, udp_port=udp_port)
        logger.info('InfluxDB Client Created for UDP Sending')
    except InfluxDBClientError as e:
        logger.exception('Exception while InfluxDB Client Creation for UDP')
        raise(e)

    # dict layout for UDP Packet
    measurement = {
        "tags": {
            "type": "RMC",
        },
        "points": [
            {
                "measurement": "gps",
                "fields": {
                    "lat": 0.0,
                    "lon": 0.0,
                    "sog": 0.0,
                    "cog": 0.0,
                    "status": 0
                }
            }
        ]
    }
    logger.debug(measurement)
    global com
    reader = pynmea2.NMEAStreamReader(errors='ignore')
    try:
        com = serial.Serial(serialport, baudrate, timeout=5.0)
        logger.info('Created Connection to Serial Port')

    except serial.SerialException as e:
        logger.exception('Exception Occured while Creation of SerialPort Connection')
        raise(e)

    while True:
        try:
            data = com.read(16).decode('utf-8')
        except Exception as e:
            logger.exception('Exception while Reading from Serial Port')
            pass

        for msg in reader.next(data):
            dat = pynmea2.parse(str(msg).strip('\r\n'), check=True)
            print(dat)
            try:
                if not (dat.latitude == 0.0 and dat.longitude == 0.0):
                    if isinstance(dat, pynmea2.RMC):
                        
                        measurement["points"][0]["fields"]["lat"] = dat.latitude
                        measurement["points"][0]["fields"]["lon"] = dat.longitude
                        measurement["points"][0]["fields"]["sog"] = dat.spd_over_grnd
                        measurement["points"][0]["fields"]["cog"] = dat.true_course
                        measurement["time"] = time.time()
                        try:
                            client.send_packet(measurement)
                        except InfluxDBClientError as e:
                            logger.exception('Exception Occured while Sending UDP Packet')
                            raise(e)
                else:
                    print("GPS Location not yet available.")
            except Exception as e:
                pass

def parse_args():
    """Pass Arguments if passed else use configuration file"""

    parser = argparse.ArgumentParser(description='CLI for acquiring GPS values and storing it in InfluxDB')

    parser.add_argument('--serialport', type=str, required=False, help='Serial Port for GPS Module')

    parser.add_argument('--baudrate', type=int, required=False, default=9600, help='Baud Rate for GPS Module Default: 9600')

    parser.add_argument('--updaterate', type=int, required=False, default=1000, help='Update Rate for GPS Module in ms. Default: 1000ms')

    parser.add_argument('--db-host', type=str, required=False, default='localhost',
                        help='hostname for InfluxDB HTTP Instance. Default: localhost')

    parser.add_argument('--db-port', type=int, required=False, default=8086,
                        help='port number for InfluxDB HTTP Instance. Default: 8086')

    parser.add_argument('--udp-port', type=int, required=False,
                        help='UDP Port for sending information via UDP.\n Should also be configured in InfluxDB')

    return parser.parse_args()

def main():
    args = parse_args()
    # print(args)
    CONF = dict()

    if len(sys.argv) == 1:
        logger.debug('Starting Script in Default Mode. Reading Conf File in %s' %CONF_PATH)

        with open(CONF_PATH) as cFile:
            _conf = json.load(cFile)
            CONF = _conf['gps'] # store conf for GPS
            logger.debug('CONF: ' + json.dumps(CONF))

        try:
            send_data(serialport = CONF['serialport'],
                      baudrate=CONF['baudrate'],
                      updaterate=CONF['updaterate'],
                      db_host=args.db_host,
                      db_port=args.db_port,
                      udp_port=CONF['dbConf']['udp_port']
                      )
        except KeyboardInterrupt:
            logger.exception('CTRL+C hit for Default Configuration')
            com.close()
            client.close()
            sys.exit(0)

    elif len(sys.argv) > 1:
        if args.serialport is None:
            print('Please Mention SerialPort for GPS Module')
            sys.exit(1)
        if args.udp_port == None:
            print('Please Mention UDP Port for Sending Values')
            sys.exit(1)
        print('Starting Script with Custom Arguments')
        try:
            send_data(serialport = args.serialport,
                        baudrate=args.baudrate,
                        updaterate=args.updaterate,
                        db_host=args.db_host,
                        db_port=args.db_port,
                        udp_port=args.udp_port)
        except KeyboardInterrupt:
            logger.exception('CTRL+C hit for Default Configuration')
            com.close()
            client.close()
            sys.exit(0)


if __name__ == '__main__':
    main()
