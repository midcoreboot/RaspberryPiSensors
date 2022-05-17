from datetime import datetime
import json

class Observation():
    def __init__(self, observationTime, numericValue, stringValue, booleanValue, sensorId):
        self.observationTime = observationTime.strftime("%m/%d/%Y, %H:%M:%S")
        self.Value = numericValue
        self.valueString = stringValue
        self.valueBoolean = booleanValue
        self.sensorId = sensorId

class RecEdgeMessage():
    def __init__(self, deviceId, observations):
        self.format = "rec3.2"
        self.deviceId = deviceId
        self.observations = observations
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    
