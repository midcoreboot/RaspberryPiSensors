#!/usr/bin/env python3
 
import pygatt, time, os, json
import logging
import threading
import traceback
import datetime
from azure.iot.device import IoTHubDeviceClient, Message
from REC import RecEdgeMessage, Observation

class HR():
    def __init__(self):
        self.address       = ""
        self.model_uid     = "00002a24-0000-1000-8000-00805f9b34fb"
        self.battery_uid   = "00002a19-0000-1000-8000-00805f9b34fb"
        self.heartbeat_uid = "00002a37-0000-1000-8000-00805f9b34fb"
        self.hr = 0
        self.startflag = False

    def start(self):        
        os.system("sudo python scan.py")
        with open("scan.txt", "r") as f:
            self.address = f.readline()
        if not self.address:
            return
        print("running with {}".format(self.address))
        self.startflag = True
        x = threading.Thread(target=self.heart_data)
        x.start()

    def heart_data(self):
        adapter = pygatt.GATTToolBackend() # for posix compliant os'ses
        
        try:
            adapter.start()
            device = adapter.connect(self.address, timeout=15)
            model = device.char_read(self.model_uid).decode("utf-8")
            battery = device.char_read(self.battery_uid)[0]
            print("device: {:s}, battery {:d}%, press enter to stop recording heart rate".format(model, battery))
            device.subscribe(self.heartbeat_uid, callback=lambda handle, value: self.devicedata(value[1]))
            input()
        finally:
            adapter.stop()
        

    def devicedata(self, data):
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
                client.send_message(message)
                print ( "Message {} successfully sent".format(message))    
            else:
                print("No message was sent since the HR was at 0")
        except:
            print(traceback.format_exc())
            print ( "IoTHubClient sample stopped" )

hr = HR()
CONNECTION_STRING = "HostName=livinglab.azure-devices.net;DeviceId=adyashaheartrate;SharedAccessKey=usYjTnlycijFApxdxLqQBDWo4kSZ0ogL/LuD+oBbFOs="
#CONNECTION_STRING = "HostName=heartrate.azure-devices.net;DeviceId=demoDevice;SharedAccessKey=IGc1Sww/ibfCjidrr+P9ATez+FcSEh64iplN88vbRzY="
client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
while True:
    hr.read(client)
    time.sleep(1)
