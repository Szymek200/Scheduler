from calendar import Calendar
import json

class Place:

    #class variable

    availableId = 1


    def __init__(self, name, address):
        self.name = name
        self.address = address
        self.id = self.availableId

        self.availableId += 1
        self.rules = []
        self.schedule = []

    
    def serializer(self):
        return{
            "__type__": "Place",
            "name": self.name,
            "address":self.address,
            "id":self.id,
            "rules":[rule.serializer() for rule in self.rules],
            "schedule":self.schedule
            
        }
        

    def addRequestedSchedule(self, rqSchedule):

        if isinstance(rqSchedule, Calendar):
            self.schedule = rqSchedule
    
    def compliesRules(self, shift, worker):
        for rule in self.rules:
            if not rule.isFulfilled():
                return False
        return True   
    
    def addRule(self, rule):
        self.rules.append(rule)

    def availableShift(self, argShift):
        for shift in self.schedule:
            #we need cast because generally there is worker 
            if shift.sameShift(argShift):
                return True
            return False

    #we add worker to the shift
    def addWorkerShift(self, argShift):
        for shift in self.schedule:
            #we need cast because generally there is worker 
            if shift.sameShift(argShift):
                #will it change value on the list?
                shift = argShift
                break

    def allShiftsOccupied(self):
        self.schedule.sort(key=lambda x: (x.worker is not None, x.begin))
        if self.schedule.first.worker == None:
            return False
        return True
    
    def serializer(self):
        return{
            "__type__": "Place",
            "name": self.name,
            "address": self.address,
            "id": self.id,
            "rules": [rule.serializer() for rule in self.rules]
        }
