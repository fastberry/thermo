# -*- coding: utf-8 -*- import os import time

#
# Python 2 Program to use temperature sensors DS18B20 on Raspberry to measure,
# temperature values.  The program automatically discovers all sensors on W1.  It
# measures data every 5 s second, displays the data and also attemptsa to send to
# a web service (seperate project)
# Author:  Andreas Bauer
# e-mail:  fastberrypi@gmail.com
# Last update: 4/21/2017

#import os and time modules
import os
import time
import requests
import json
import datetime


#
# some global variables
#

# path for devices on W1 on the system bus
devicePath = '/sys/bus/w1/devices/'
sensors = []

# start id value.  The ID count is incremented for each data record sent to the web service
idCount = 100

#
# the class TempSensor is used to keep static information about each temperature sensor
# and offers a method to access the current value
#
class TempSensor:
    'Temperator sensor class with information about sensor and capability to read current value'

    # the class data
    name = ''
    fullPath = ''
    niceName = ''
    value = 0.0
    lastRead = ''

    # constructor; it initializes all data members per passed parameters
    def __init__ (self, name, fullPath, niceName):
        self.name = name
        self.fullPath = fullPath
        self.niceName = niceName
        self.value = 0.0
        self.lastRead = ''

    # print instance data.  Used for debugging and diagnosis purposes
    def dump(self):
        print "Name: %s Full Path: %s Nice Name: %s Value: %3.2f Last Read: %s" \
        % (self.name, self.fullPath, self.niceName, self.value, self.lastRead)

    # read temperature from file in raw format
    def tempFileRead(self):
        f = open(self.fullPath, 'r')
        lines = f.readlines()
        f.close()
        return lines

    # read the sensor
    def read(self):

        # read the sensor file
        lines = self.tempFileRead()

        # wait until new data is available
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = self.tempFileRead()

        # get the relevant portion of the file content
        temp_output = lines[1].find('t=')

        if temp_output != -1:
            temp_string = lines[1].strip()[temp_output+2:]
            temp_c = float(temp_string) / 1000.0
            temp_f = temp_c * 9.0 / 5.0 + 32.0
            self.value = temp_f
            dateValue = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.lastRead = dateValue
            return temp_f

    # send the data values to the temperature data service via REST
    def send_to_dataservice(self):
            parameters = {'id': idCount,
                    'sensorName': self.name,
                    'dateWritten': self.lastRead,
                    'temperatureValue': self.value}
            response = requests.post('http://andydevubu:8080/EnvironmentDataService/rest/TemperatureRecordService/temperatureRecords',
                parameters, auth=('', ''))
            idCount += 1

            # for debugging the following two lines can be uncommented
            # print 'Post Request'
            # print response.content

#
# class to implement service that manages all sensors
#

class TemperatureService:
    'Service to manage and read temperature sensors'

    # the class data
    # list of all temperature sensors
    sensors = []

    # constructor; it initializes all data members per passed parameters
    def __init__ (self):
        self.discoverSensors()

    # print instance data.  Used for debugging and diagnosis purposes
    def dump(self):
        for sensor in sensors:
            sensor.dump()
        
    # initialize to access the sensors and discover them al
    def discoverSensors(self):
  
        # load kernel modules
        os.system('modprobe w1-gpio')
        os.system('modprobe w1-therm')

        # get the contents of the bus directory.  listdir will give us a list of all sensor file names.
        sensorFileNames = os.listdir(devicePath);
        count = 1
        for sensorFileName in sensorFileNames:

            # our sensor has the prefix "28-"
            if '28-' in sensorFileName:
                fullPath = devicePath + sensorFileName + '/w1_slave'
                newNiceName = 'Sensor ' + str(count)
                count += 1
                newSensor = TempSensor(sensorFileName, fullPath, newNiceName)
                sensors.append(newSensor)

    # read the sensors
    def readSensors(self):
        for sensor in sensors:
            sensor.read()
   

# create a service instance
temperatureService = TemperatureService()

# keep running until ctrl+C
while True:
    temperatureService.readSensors()
    temperatureService.dump()
    time.sleep(5)


