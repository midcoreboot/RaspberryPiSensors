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
        self.address       = ""
        self.hrService = "0000180d-0000-1000-8000-00805f9b34fb"
        self.peripheral = btle.Peripheral()
        self.isConnected = False
        self.hr = 0
        self.lastHr = 0
        self.startflag = False
 
    def start(self):        
        os.system("sudo python scan.py")
        with open("scan.txt", "r") as f:
            self.address = f.readline()
        if not self.address:
            return
        print("running with {}".format(self.address))
        self.startflag = True
        self.heart_data()
 
    def heart_data(self):
        try:
            print("Connecting to address.")
            self.peripheral.connect(self.address)
            self.peripheral.setDelegate(MyDelegate())
            svc = self.peripheral.getServiceByUUID(btle.UUID(self.hrService))
            ch = svc.getCharacteristics()[0]
            print(ch.valHandle)
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
CONNECTION_STRING = "HostName=JTH-Smart-Space-Hub.azure-devices.net;DeviceId=HeartrateSensor;SharedAccessKey=Pi0XpNeeuiCFkeFbBTPvSMonwws+kQFEQT87hww1LNM="
 
class MyDelegate(btle.DefaultDelegate):
    def __init__(self):
        btle.DefaultDelegate.__init__(self)
    def handleNotification(self, cHandle, data):
        intData = int.from_bytes(data, "big")
        print("Notif received: {}".format(intData))
        hr.devicedata(intData)
 
client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
while True:
    print("Waiting....")
    time.sleep(1)
    print("test {}".format(hr.read(client)))
    if hr.isConnected == True:
        if hr.peripheral.waitForNotifications(0):
            continue
 