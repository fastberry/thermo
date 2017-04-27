#!/usr/bin/python3

#
# Python 2 Program to use temperature sensors DS18B20 on Raspberry to measure,
# temperature values.  The program automatically discovers all sensors
# that are connected.  
# Author:  Andreas Bauer
# e-mail:  fastberrypi@gmail.com
# Last update: 4/21/2017

# import required modules for os, time and regular expressions
import os
import time
import re

# global variables

# path for devices on W1 on the system bus
devicePath = '/sys/bus/w1/devices/'
webPagePath = '/home/pi/web/index.html'
sensors = []

# function to convert degrees Celsius to degrees Fahrenheit

def celsiusToFahrenheit(celsiusValue) :
    return celsiusValue * 9 / 5 + 32

# the class TempSensor is used to keep the access information for each
# sensor and has the method to read the temperature from the sensor
class TempSensor:
    'Temperator sensor class with information about sensor and capability to read current value'

    # the class data
    name = ''
    fullPath = ''
    niceName = ''
    value = 0.0

    # constructor; it initializes all data members per passed parameters
    def __init__ (self, name, fullPath, niceName):
        self.name = name
        self.fullPath = fullPath
        self.niceName = niceName
        self.value = 0.0

    # print instance data.  Used for debugging and diagnosis purposes
    def display(self):
        print ("%s: %3.2f" % (self.niceName, self.value))

    # read temperature from file in raw format
    def tempFileRead(self):
        f = open(self.fullPath, 'r')
        text = f.readlines()
        f.close()
        return text

    # read the sensor
    def read(self):

        # read the sensor file
        text = self.tempFileRead()

        # wait until valid data is available by checking until the
        # substring "YES" is in the first line of the text
        while 'YES' not in text[0]:
            time.sleep(0.2)
            text = self.tempFileRead()
            print (text)

        # get the relevant portion of the file content
        tempValueString = text[1].split("t=")[1]
        
        if re.match("[0123456789]*", tempValueString):
            self.value = celsiusToFahrenheit(float(tempValueString) / 1000.0)

# class to manage all sensors
class TemperatureService:
    'Service to manage and read temperature sensors'

    # the class data
    # list of all temperature sensors
    sensors = []

    # constructor; it initializes all data members per passed parameters
    def __init__ (self):
        self.discoverSensors()

    # print instance data.  Used for debugging and diagnosis purposes
    def display(self):
        for sensor in self.sensors:
            sensor.display()
        
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
                self.sensors.append(newSensor)

    # read the sensors
    def readSensors(self):
        for sensor in self.sensors:
            sensor.read()


# create a service instance
temperatureService = TemperatureService()

# keep running until ctrl+C
while True:
    temperatureService.readSensors()
    temperatureService.display()
    time.sleep(1)
