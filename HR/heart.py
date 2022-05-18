#!/usr/bin/env python3
 
import time, os, json
from bluepy import btle
import binascii
import logging
import threading
import traceback
from datetime import datetime
from azure.iot.device import IoTHubDeviceClient, Message
from REC import Observation, RecEdgeMessage
 
class HR():
    def __init__(self):
        # Set the mac address of the sensor for this raspberry pi.
        self.address       = ""
        self.hrService = "0000180d-0000-1000-8000-00805f9b34fb"
        self.peripheral = btle.Peripheral()
        self.isConnected = False
        self.hr = 0
        self.lastHr = 0
        self.startflag = False
 
    def start(self):
        if not self.address:
            print("Please chose an address to the HR sensor.")
            return
        print("running with {}".format(self.address))
        self.startflag = True
        self.heart_data()
 
    def heart_data(self):
        try:
            print("Connecting to address.")
            self.peripheral.connect(self.address)
            #Set the delegate to the one created.
            self.peripheral.setDelegate(MyDelegate())
            #Get the HR measurement service
            svc = self.peripheral.getServiceByUUID(btle.UUID(self.hrService))
            #Get the HR characteristic.
            ch = svc.getCharacteristics()[0]
            #Tell the characteristic we want to be subscribed to it
            self.peripheral.writeCharacteristic(ch.valHandle+1, b"\x01\00")
            self.isConnected = True
        except Exception as E:
            self.peripheral.disconnect()
            print("exception caught")
 
 
    def devicedata(self, data):
        print("subscription gave: {}".format(data))
        self.hr = data
 
    def read(self, client):
        if not self.startflag:
            self.start()
        self.send_to_azure(client)
        return ({'hr': self.hr})
 
    def send_to_azure(self, client):
        try:
            if self.hr != 0:
                #Change "heartrateTest to the digital twin id of the sensor."
                observation = Observation(datetime.now(), self.hr, None, None, "heartrateTest")
                rec = RecEdgeMessage(None, [observation])
                recJSON = rec.toJSON()
                message = Message(recJSON.encode('ascii'))
                message.content_encoding = "utf-8"
                message.content_type = "application/json"
                #client.send_message(message)
                #print ( "Message {} successfully sent".format(message))    
            else:
                print("No message was sent since the HR was at 0")
        except:
            print(traceback.format_exc())
            print ( "IoTHubClient sample stopped" )
 
hr = HR()
#Change to the sensors IoT device connection string
CONNECTION_STRING = "HostName=JTH-Smart-Space-Hub.azure-devices.net;DeviceId=HeartrateSensor;SharedAccessKey=Pi0XpNeeuiCFkeFbBTPvSMonwws+kQFEQT87hww1LNM="
 
class MyDelegate(btle.DefaultDelegate):
    def __init__(self):
        btle.DefaultDelegate.__init__(self)
    def handleNotification(self, cHandle, data):
        intData = int.from_bytes(data, "big")
        hr.devicedata(intData)
 
client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
while True:
    if hr.isConnected == True:
        print("Waiting....")
        if hr.peripheral.waitForNotifications(2.0):
            print("HR {}".format(hr.read(client)))
            time.sleep(2)
            continue
    else:
        print("HR {}".format(hr.read(client)))
        time.sleep(5)
 