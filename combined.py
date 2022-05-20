#!/usr/bin/python3
import sys
import time
from datetime import datetime
from grove.adc import ADC
from bluepy import btle
import traceback
from datetime import datetime
from REC import Observation, RecEdgeMessage
from azure.iot.device import IoTHubDeviceClient, Message
import logging

#Put the IoT Hub device connection string here.
#The deviceId should be the raspberry pi's MAC address.
CONNECTION_STRING = "HostName=JTH-Smart-Space-Hub.azure-devices.net;DeviceId=b827ebac49b6;SharedAccessKey=TqC/e8lpRbhlDOrtAnyBX/1tqRSAtdLjbaTw15Byi7k="

class Grove:
    def __init__(self, channel):
        self.channel = channel
        self.adc = ADC()
    
    @property
    def GSR(self):
        value = self.adc.read(self.channel)
        return value

class HR():
    def __init__(self):
        # Set the mac address of the HR sensor for this raspberry pi.
        self.address = "A0:9E:1A:A4:22:ED"
        self.hrService = "0000180d-0000-1000-8000-00805f9b34fb"
        #Peripheral is the bluepy object we use to communicate with the sensor via BT
        self.peripheral = btle.Peripheral()
        self.isConnected = False
        self.hr = 0
        self.startflag = False
 
    def start(self):
        if not self.address:
            print("Please choose an address to the HR sensor.")
            return
        print("running with {}".format(self.address))
        self.startflag = True
        self.heart_data()
 
    def heart_data(self):
        try:
            print("Connecting to address {}.".format(self.address))
            self.peripheral.connect(self.address)
            #Set the delegate to the one created.
            self.peripheral.setDelegate(MyDelegate())
            #Get the HR measurement service
            svc = self.peripheral.getServiceByUUID(btle.UUID(self.hrService))
            #Get the HR characteristic.
            ch = svc.getCharacteristics()[0]
            #Tell the characteristic we want to be subscribed to it
            self.peripheral.writeCharacteristic(ch.valHandle+1, b"\x01\00")
            time.sleep(3)
            self.isConnected = True
        except:
            self.startflag = False
            self.isConnected = True
            print(traceback.format_exc())
            print("exception caught")
 
 
    def devicedata(self, data):
        print("subscription gave: {}".format(data))
        self.hr = data
 
    def read(self):
        print(self.startflag)
        if not self.startflag:
            self.start()
        return self.hr

client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
hr = HR()
# The parameter here is the ADC channel the GSR sensor is connected on. 0 is the A0.
gsr = Grove(0)

class MyDelegate(btle.DefaultDelegate):
    def __init__(self):
        btle.DefaultDelegate.__init__(self)
    def handleNotification(self, cHandle, data):
        #this is the code that is ran when we get an HR measurement notification.
        intData = int.from_bytes(data, "big")
        hr.devicedata(intData)

try:
    #Wait for the os to stabilize after bootup.
    time.sleep(10)
    while True:
        if hr.isConnected == True:
            if hr.peripheral.waitForNotifications(2.0):
                #Change "heartrateTest" to the digital twin id of the HR sensor.
                hrObservation = Observation(datetime.now(), hr.read(), None, None, "b827ebac49b6-hr")
                #Change "GSR Sensor" to the digital twin id of the GSR sensor.
                gsrObservation = Observation(datetime.now(), gsr.GSR, None, None, "b827ebac49b6-gsr")
                rec = RecEdgeMessage(None, [hrObservation, gsrObservation])
                recJSON = rec.toJSON()
                message = Message(recJSON.encode('ascii'))
                message.content_encoding = "utf-8"
                message.content_type = "application/json"
                client.send_message(message)
                print("Sent message to IOT hub: {}".format(recJSON))
                time.sleep(2)
                continue
        else:
            print("Connecting to HR sensor..")
            print("HR {}".format(hr.read()))
            time.sleep(10)
except:
    print(traceback.format_exc())
    print("Sensor.service caught an critical error.")

