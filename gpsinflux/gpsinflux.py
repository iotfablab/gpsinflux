#!/usr/bin/env python3
# Python3 Command Line Utility to read from MTK GPS Module (Adafruit) connected
# to serial ports and store GPS relevant information to InfluxDB via UDP and
# publishing the data to MQTT topics
# Author: Shantanoo Desai <des@biba.uni-bremen.de>
# Changes:
# - Change `measurement` dict
# - Create Line Protocol Strings from `measurement` dict
# - Add Multiple Publishing to respective MQTT Topics

import os
import sys
import logging
import json
import time
import argparse
import concurrent.futures
import serial
import pynmea2
from .mt3339 import mt3339
from influxdb import InfluxDBClient, line_protocol
from influxdb.client import InfluxDBClientError
import paho.mqtt.publish as publish

# Logger Settings
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

handler = logging.FileHandler("/var/log/gpsinflux.log")
handler.setLevel(logging.ERROR)

formatter = logging.Formatter('%(asctime)s-%(name)s-%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

DEVICE = ''
com = None
client = None
gps_conf = dict()
mqtt_conf = dict()


def gps_setup(serialport, baudrate, updaterate):
    """ Setup GPS Device Baud and Update Rates and
        read only RMC Sentences"""
    try:
        gps = mt3339(serialport)
        gps.set_baudrate(baudrate)
        gps.set_nmea_update_rate(updaterate)
        gps.set_nmea_output(gll=0, rmc=3, vtg=0, gga=0, gsa=0, gsv=0)
    except Exception as e:
        print('Exception Occured while setting up GPS')
        raise(e)


def publish_data(lineprotocol_data):
    """ Publish Data points as line protocol strings to MQTT Broker
    """
    lp_array = lineprotocol_data.split('\n')
    lp_array.pop()  # remove the last newline from the array
    publish_messages = []
    global gps_conf
    global mqtt_conf
    for topic in gps_conf['topics']:
        mqtt_msg = {
            'topic': DEVICE + '/' + topic,
            'payload': lp_array[gps_conf['topics'].index(topic)],
            'qos': 1,
            'retain': False
        }
        publish_messages.append(mqtt_msg)
    logger.debug(publish_messages)
    try:
        publish.multiple(
            publish_messages,
            hostname=mqtt_conf['broker'],
            port=mqtt_conf['port'])
        return True
    except Exception as e:
        logger.error(e)
        return False


def save_to_db(measurements):
    """Save Data to InfluxDB
    """
    global client
    try:
        client.send_packet(measurements)
        return True
    except InfluxDBClientError as influx_e:
        logger.error('Error while UDP sending: {e}'.format(e=influx_e))
        return False


def read_from_gps(serialport, baudrate, updaterate):
    logger.info('Setting Up GPS')
    # NOTE: Comment the line below out when using Adafruit GPS Wing
    # gps_setup(serialport, baudrate, updaterate)
    global DEVICE
    # dict layout for UDP Packet
    measurement = {
        "tags": {
            "source": "gps"
        },
        "points": [
            {
                "measurement": "location",
                "fields": {
                        "lat": 0.0
                }
            },
            {
                "measurement": "location",
                "fields": {
                    "lon": 0.0
                }
            },
            {
                "measurement": "groundVelocity",
                "fields": {
                        "sog": 0.0
                }
            },
            {
                "measurement": "groundVelocity",
                "fields": {
                        "cog": 0.0
                }
            }
        ]
    }

    # Create Serial Connection and NMEA Stream Reader /Parser
    global com
    reader = pynmea2.NMEAStreamReader(errors='ignore')
    com = serial.Serial(serialport, baudrate, timeout=5.0)
    logger.info('Created Connection to Serial Port')

    while True:
        try:
            data = com.read(16).decode('utf-8')
            for msg in reader.next(data):
                dat = pynmea2.parse(str(msg).strip('\r\n'), check=True)
                logger.debug('NMEA Sentence: {d}'.format(d=dat))
                try:
                    if not (dat.latitude == 0.0 and dat.longitude == 0.0):
                        if isinstance(dat, pynmea2.RMC):
                            timestamp = int(time.time())
                            measurement["points"][0]["fields"]["lat"] = dat.latitude
                            measurement["points"][1]["fields"]["lon"] = dat.longitude
                            measurement["points"][2]["fields"]["sog"] = dat.spd_over_grnd
                            measurement["points"][3]["fields"]["cog"] = dat.true_course
                            for point in measurement['points']:
                                # insert timestamp to each point
                                point['time'] = timestamp
                            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                                if executor.submit(publish_data, line_protocol.make_lines(measurement)).result():
                                    logger.info('MQTT Publish Success')
                                if executor.submit(save_to_db, measurement).result():
                                    logger.info('Data saved to InfluxDB')
                    else:
                        logger.info("GPS Location not yet available.")
                except Exception as e:
                    logger.error(e)
        except Exception as e:
            logger.error('Exception Serial Port Read: {e}'.format(e=e))
            com.close()
            client.close()
            sys.exit(2)


def file_path(path_to_file):
    """Check if Path and File exist for Configuration"""

    if os.path.exists(path_to_file):
        if os.path.isfile(path_to_file):
            logger.info('File Exists')
            with open(path_to_file) as conf_file:
                return json.load(conf_file)
        else:
            logger.error('Configuration File Not Found')
            raise FileNotFoundError(path_to_file)
    else:
        logger.error('Path to Configuration File Not Found')
        raise NotADirectoryError(path_to_file)


def parse_args():
    """Pass Arguments for configuration file"""

    parser = argparse.ArgumentParser(description='CLI for acquiring GPS values, storing it in InfluxDB and publishing via MQTT')
    parser.add_argument('--config', type=str, required=True, help='configuration conf.json file with path.')

    return parser.parse_args()


def main():
    """Initial Setup of Clients based on Configuration File"""
    args = parse_args()
    # print(args)
    CONF = file_path(args.config)
    global gps_conf
    gps_conf = CONF['gps']
    influx_conf = CONF['influx']

    global mqtt_conf
    mqtt_conf = CONF['mqtt']

    global DEVICE
    DEVICE = CONF['deviceID']

    logger.info('Creating InfluxDB Client')
    logger.debug('Client for {influx_host}@{influx_port} with udp:{udp_port}'.format(
        influx_host=influx_conf['host'],
        influx_port=influx_conf['port'],
        udp_port=gps_conf['udp_port']))
    global client
    client = InfluxDBClient(
        host=influx_conf['host'],
        port=influx_conf['port'],
        use_udp=True,
        udp_port=gps_conf['udp_port'])
    logger.info('Checking Connectivity to InfluxDB')
    try:
        if client.ping():
            logger.info('Connected to InfluxDB')
        else:
            logger.error('Cannot Connect to InfluxDB. Check Configuration/Connectivity')
    except Exception as connection_e:
        logger.error(connection_e)
        client.close()
        sys.exit(1)

    logger.info('Connecting to GPS Device')
    logger.debug('Device @ {port}, with baud={baud} & update={upd}'.format(
        port=gps_conf['serialport'],
        baud=gps_conf['baudrate'],
        upd=gps_conf['updaterate']))
    try:
        read_from_gps(
            serialport=gps_conf['serialport'],
            baudrate=gps_conf['baudrate'],
            updaterate=gps_conf['updaterate'])
    except KeyboardInterrupt:
        print('CTRL+C hit for Default Configuration')
        com.close()
        client.close()
        sys.exit(0)


if __name__ == '__main__':
    main()
