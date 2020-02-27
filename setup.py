from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(name='gpsinflux',
      version='1.5',
      description='Extract GPS values and store into InfluxDB and publish via MQTT',
      long_description=readme(),
      url='https://github.com/iotfablab/gpsinflux',
      author='Shantanoo Desai',
      author_email='des@biba.uni-bremen.de',
      license='MIT & LGPLv3',
      packages=['gpsinflux'],
      scripts=['bin/gpsinflux'],
      install_requires=[
            'pynmea2',
            'pyserial',
            'influxdb',
            'paho-mqtt'
      ],
      include_data_package=True,
      zip_safe=False)
