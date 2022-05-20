## Main.py
import RPi.GPIO as GPIO
import time
from datetime import datetime
from REC import Observation, RecEdgeMessage
from azure.iot.device import IoTHubDeviceClient, Message
 
 
RECIEVED_MESSAGES = 0
 
def main():
    try:
        GPIO.setmode(GPIO.BCM)
        #red = 18
        button = 15
        #GPIO.setup(red, GPIO.OUT)
        GPIO.setup(button, GPIO.IN)
 
        lampOn = False
        lastValue = 0
        CONNECTION_STRING = "HostName=JTH-Smart-Space-Hub.azure-devices.net;DeviceId=lightSwitch;SharedAccessKey=wS9OQCP57tQBKt4DFjcl4zNt3fNpaOYSXsO2y4vJL8M="
        client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
        client.on_message_received = message_handler
        while(True):
            #try:
                value = GPIO.input(button)
                #print("Value of button: {}".format(value))
                if lastValue != value:
                    if value == 1:
                        lampOn = not lampOn
                        observation = Observation(datetime.now(), None, None, lampOn, "lightSwitch")
                        rec = RecEdgeMessage(None, [observation])
                        print(rec)
                        recJSON = rec.toJSON()
                        message = Message(recJSON.encode('ascii'))
                        message.content_encoding = "utf-8"
                        message.content_type = "application/json"
                        client.send_message(message )
                        print("Sent message: {}".format(message))
 
                        print("lamp on is now: {}".format(lampOn))
                lastValue = value
                #if lampOn:
                #    GPIO.output(red, GPIO.HIGH)
                #else:
                #    GPIO.output(red, GPIO.LOW)
                time.sleep(0.3)
            #except:
            #    print("unexplained crash")
            #    GPIO.cleanup()
            #    break
    except KeyboardInterrupt:
        GPIO.cleanup()
        client.shutdown()
 
 
def message_handler(message):
    global RECIEVED_MESSAGES
    RECIEVED_MESSAGES+=1
    print("")
    print("Message recieved: ")
    for property in vars(message).items():
        print("    {}".format(property))
    print("Total calls recieved on device: {}".format(RECIEVED_MESSAGES))
 
if __name__ == '__main__':
    main()