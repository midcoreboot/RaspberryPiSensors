import time, os, json
import traceback
import random
from datetime import datetime
from REC import Observation, RecEdgeMessage
from azure.iot.device import IoTHubDeviceClient, Message

CONNECTION_STRING = "HostName=JTH-Smart-Space-Hub.azure-devices.net;DeviceId=HeartrateSensor;SharedAccessKey=Pi0XpNeeuiCFkeFbBTPvSMonwws+kQFEQT87hww1LNM="

client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
for x in range(2):
    try:
        heartrate = random.randrange(60, 180)
        observation = Observation(datetime.now(), heartrate, None, None, "heartrateTest")
        rec = RecEdgeMessage(None, [observation])
        recJSON = rec.toJSON()
        message = Message(recJSON.encode('ascii'))
        message.content_encoding = "utf-8"
        message.content_type = "application/json"
        #print("MESSAGE: {}".format(message))
        print("REC: {}".format(recJSON))
        time.sleep(1)
        client.send_message(message)
        print("Message {} sent to twin".format(message))
    except:
        print(traceback.format_exc())
        print("stopped")