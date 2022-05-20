#light.py
import RPi.GPIO as GPIO
import time
from datetime import datetime
from REC import Observation, RecEdgeMessage
from azure.iot.device import IoTHubDeviceClient, Message
 
RECIEVED_MESSAGES = 0
red = 18
 
def message_handler(message):
    global RECIEVED_MESSAGES
    RECIEVED_MESSAGES+=1
    print("Message recieved: {}".format(message))
    # Convert iot.device.message to bytearray
    bytes = bytearray(message.data)
    #Decode the bytearray
    if bytes.decode() == "True":
        output = GPIO.HIGH
    elif bytes.decode() == "False":
        output = GPIO.LOW
    else:
        return
    GPIO.output(red, output)
    print("Total calls recieved on device: {}".format(RECIEVED_MESSAGES))
 
def main():
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(red, GPIO.OUT)
        CONNECTION_STRING = "HostName=JTH-Smart-Space-Hub.azure-devices.net;DeviceId=lightSwitch-Light;SharedAccessKey=SKLjYQ5ilJZ78UJajWiccTPRecoiad6o3YgqRO1SQfA="
        client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
        client.on_message_received = message_handler
        print("Waiting to receive messages from cloud...")
        while(True):
            time.sleep(500)
    except KeyboardInterrupt:
        client.shutdown()
        GPIO.cleanup()
 
if __name__ == '__main__':
    main()