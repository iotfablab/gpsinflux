# gpsinflux

Command-Line-Utility written in Python3.x for obtaining information via
MTK GPS Modules and storing information (GPRMC) to InfluxDB via UDP and publish data to MQTT.


## Installation

clone the repository to your machine and use `pip` to install the CLI:

    pip install .

## Usage

__LINUX__: In order to use this script you need `sudo` rights to open a serial port. (See Development)

__WINDOWS__: use `COMx` where `x` is the number of the serial port available through the Device Manager


```bash
usage: gpsinflux [-h] --config CONFIG

CLI for acquiring GPS values and storing it in InfluxDB and publishing data to MQTT

optional arguments:
  -h, --help       show this help message and exit
  --config CONFIG  configuration conf.json file with path.
```

A Configuration File `conf.json` is needed with the path to the file as an argument to run the script.

    gpsinflux --config /etc/test/conf.json

Refer to `conf.json` for structure.

## MQTT Publishing
Topics on which data is published is as follows:

```
<device_ID>/location/gps/latitude
<device_ID>/location/gps/longitude
<device_ID>/groundVelocity/gps/sog
<device_ID>/groundVelocity/gps/cog
```
Data Format will be InfluxDB's Line Protocol

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

### License Disclaimers

The Repository is published under the MIT License.

The file `mt3339.py` is published under the __GNU Lesser General Public License v3__. 
The Copy of the License and Notice is added to the respective file and within this repository.