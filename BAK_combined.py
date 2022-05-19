import sys
import time
from datetime import datetime
from grove.adc import ADC
from bluepy import btle
import traceback
from datetime import datetime
from REC import Observation, RecEdgeMessage
from azure.iot.device import IoTHubDeviceClient, Message

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
        # Set the mac address of the HR  sensor for this raspberry pi.
        self.address = "A0:9E:1A:A4:22:ED"
        self.hrService = "0000180d-0000-1000-8000-00805f9b34fb"
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
            time.sleep(3)
            self.isConnected = True
        except Exception as E:
            self.peripheral.disconnect()
            print("exception caught")
            exit()
 
 
    def devicedata(self, data):
        print("subscription gave: {}".format(data))
        self.hr = data
 
    def read(self):
        if not self.startflag:
            self.start()
        return self.hr

client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
hr = HR()
gsr = Grove(0)

class MyDelegate(btle.DefaultDelegate):
    def __init__(self):
        btle.DefaultDelegate.__init__(self)
    def handleNotification(self, cHandle, data):
        intData = int.from_bytes(data, "big")
        hr.devicedata(intData)

try:
    while True:
        if hr.isConnected == True:
            if hr.peripheral.waitForNotifications(2.0):
                #Change "heartrateTest" to the digital twin id of the HR sensor.
                hrObservation = Observation(datetime.now(), hr.read(), None, None, "heartrateTest")
                #Change "GSR Sensor" to the digital twin id of the GSR sensor.
                gsrObservation = Observation(datetime.now(), gsr.GSR, None, None, "GSR Sensor")
                rec = RecEdgeMessage(None, [hrObservation, gsrObservation])
                recJSON = rec.toJSON()
                message = Message(recJSON.encode('ascii'))
                message.content_encoding = "utf-8"
                message.content_type = "application/json"
                #client.send_message(message)
                print("Sent message to IOT hub: {}".format(recJSON))
                time.sleep(2)
                continue
            else:
                print("jesus")
        else:
            print("Connecting to HR sensor..")
            print("HR {}".format(hr.read()))
            time.sleep(5)
except:
    print(traceback.format_exc())
    print(" SENSOR SCRIPTS CRASHED")
    sys.exit()