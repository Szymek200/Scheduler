
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

        if isinstance(rqSchedule, list):
            self.schedule = rqSchedule
    
    def compliesRules(self, shift, worker=None):
            import rules
       
            #rules specyfic for this particular place - RulePlace - all at once need to be fullfilled
            place_rules = [r for r in self.rules if isinstance(r, rules.PlaceRule)]
            for rule in place_rules:
                if not rule.isFulfilled(shift):
                    return False
                    
         
            #availability rules - for example Cyclic rule - OR
            availability_rules = [r for r in self.rules if isinstance(r, rules.Rule)]
            if availability_rules:
                passed_any = False
                for rule in availability_rules:
                    if rule.isFulfilled(shift):
                        passed_any = True
                        break
                
                #if we didn't find any complied rule -> false
                if not passed_any:
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
