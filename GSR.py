import math
import sys
import time
from datetime import datetime
from grove.adc import ADC
from REC import Observation, RecEdgeMessage
from azure.iot.device import IoTHubDeviceClient, Message

CONNECTION_STRING = "HostName=JTH-Smart-Space-Hub.azure-devices.net;DeviceId=GSRSensor;SharedAccessKey=ZdYZbEQOOGMW/etSGKfiSzJ4mLvL6o1TVdFHa0GXGvY="
client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
#Install GSR sensor on ADC channels only.

class Grove:
    def __init__(self, channel):
        self.channel = channel
        self.adc = ADC()
    
    @property
    def GSR(self):
        value = self.adc.read(self.channel)
        return value

grove = Grove

def main():
    if len(sys.argv) < 2:
        print('Usage: {} adc_channel'.format(sys.argv[0]))
        sys.exit(1)
    #Initialize sensor on the GPIO channel provided in the console args (sudo python 0 when sensor on A0)
    sensor = Grove(int(sys.argv[1]))
    print("Detecting")
    while True:
        print('GSR value: {}'.format(sensor.GSR))
        observation = Observation(datetime.now(), sensor.GSR, None, None, "GSRSensor")
        rec = RecEdgeMessage(None, [observation])
        recJSON = rec.toJSON()
        message = Message(recJSON.encode('ascii'))
        message.content_encoding = "utf-8"
        message.content_type = "application/json"
        client.send_message(message)
        print("GSR sent message: {} to IOT".format(message))
        time.sleep(3)

if __name__ == '__main__':
    main()