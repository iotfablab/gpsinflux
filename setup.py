from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='gpsinflux',
      version='0.9',
      description='Extract GPS values and store into InfluxDB',
      long_description=readme(),
      url='https://github.com/iotfablab/gpsinflux',
      author='Shantanoo Desai',
      author_email='des@biba.uni-bremen.de',
      license='MIT',
      packages=['gpsinflux'],
      scripts=['bin/gpsinflux'],
      install_requires=[
            'pynmea2',
            'pyserial',
            'influxdb'
      ],
      include_data_package=True,
      zip_safe=False)
