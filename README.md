# gpsinflux

Command-Line-Utility written in Python3.x for obtaining information via
MTK GPS Modules and storing information (GPGGA) to InfluxDB either via UDP or HTTP.


## Installation

clone the repository to your machine and use `pip` to install the CLI:

    pip install .

## Usage

__NOTE__: In order to use this script you need `sudo` rights to open a serial port.


```
    usage: gpsinflux [-h] [--serialport SERIALPORT] [--baudrate BAUDRATE]
                 [--updaterate UPDATERATE] [--http] [--db-host DB_HOST]
                 [--db-port DB_PORT] [--db-name DB_NAME] [--udp]
                 [--udp-port UDP_PORT]

    CLI for acquiring GPS values and storing it in InfluxDB

    optional arguments:
    -h, --help            show this help message and exit
    --serialport SERIALPORT
                        Serial Port for GPS Module
    --baudrate BAUDRATE   Baud Rate for GPS Module Default: 9600
    --updaterate UPDATERATE
                        Update Rate for GPS Module in ms. Default: 1000ms
    --http                Send GPS data via HTTP. Default: Disabled
    --db-host DB_HOST     hostname for InfluxDB HTTP Instance. Default:
                        localhost
    --db-port DB_PORT     port number for InfluxDB HTTP Instance. Default: 8086
    --db-name DB_NAME     database name to add GPS values to
    --udp                 Send sensor via UDP. Default: Enabled
    --udp-port UDP_PORT   UDP Port for sending information via UDP. Should also
                        be configured in InfluxDB

```


## Default

if no parameters are provided then the configuration from `/etc/umg/conf.json` is taken.

     # starts according to conf.json in /etc/umg/ folder
     # gpsinflux

Basic configuration can be found in `conf.json` file. Make sure to move this file into your `/etc` folder.


## Custom

Serial Port for the GPS device is mandatory

### UDP

1. Serial Port of the GPS Module (mandatory)

2. UDP Port value (mandatory)

        $ gpsinflux --udp --udp-port 20001 --serialport /dev/ttyUSB0


### HTTP

1. Serial Port of the GPS Module (mandatory)

2. InfluxDB Database Name (mandatory)

        $ gpsinflux --http --db-name gps --serialport /dev/ttyUSB0


## Development

Use `virtualenv` to create a test environment as follows:

    virtualenv -p python3 testenv
    . testenv/bin/activate

    pip install -e .

For Development one needs to change the serial port rights to user and `sudo` won't be very helpful.

Change the serial port's rights as follows:

    sudo chown -R <user>:<user> /dev/ttyUSB0

To exit the `virtualenv`

     deactivate

## Maintainer

* Shantanoo Desai (des@biba.uni-bremen.de)
