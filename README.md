# gpsinflux

Command-Line-Utility written in Python3.x for obtaining information via
MTK GPS Modules and storing information (GPRMC) to InfluxDB either via UDP.


## Installation

clone the repository to your machine and use `pip` to install the CLI:

    pip install .

## Usage

__NOTE__: In order to use this script you need `sudo` rights to open a serial port.


```
usage: gpsinflux [-h] [--serialport SERIALPORT] [--baudrate BAUDRATE]
               [--updaterate UPDATERATE] [--db-host DB_HOST]
               [--db-port DB_PORT] [--udp-port UDP_PORT]

CLI for acquiring GPS values and storing it in InfluxDB

optional arguments:
  -h, --help            show this help message and exit
  --serialport SERIALPORT
                        Serial Port for GPS Module
  --baudrate BAUDRATE   Baud Rate for GPS Module Default: 9600
  --updaterate UPDATERATE
                        Update Rate for GPS Module in ms. Default: 1000ms
  --db-host DB_HOST     hostname for InfluxDB. Default: `localhost`
  --db-port DB_PORT     port number for InfluxDB. Default: 8086
  --udp-port UDP_PORT   UDP Port for sending information via UDP. Should also
                        be configured in `influxdb.conf`

```


## Default

if no parameters are provided then the configuration from `/etc/umg/conf.json` is taken.

     # starts according to conf.json in `/etc/umg/` folder
     # gpsinflux

Basic configuration can be found in `conf.json` file. Make sure to move this file into your `/etc` folder.


## Custom
The `influxdb.conf` should have `[[udp]]` configured for port 20001 with a database to store the data.

    $ gpsinflux --udp-port 20001 --serialport /dev/ttyUSB0

## Development

Use `virtualenv` to create a test environment as follows:

    python -m venv venv
    . venv/bin/activate

    pip install -e .

For Development one needs to change the serial port rights to user and `sudo` won't be very helpful.

Change the serial port's rights as follows:

    sudo chown -R <user>:<user> /dev/ttyUSB0

To exit the `virtualenv`

     deactivate

## Maintainer

* Shantanoo Desai (des@biba.uni-bremen.de)
