

from datetime import timedelta
from itertools import combinations

from rules import EtatRule
import utils

from shift import ShiftPlace, Shift

class Worker:

    #class variable

    availableId = 1


    def __init__(self, name, surname, pesel):
        self.name = name
        self.surname = surname
        self.pesel = pesel

        self.id = self.availableId
        Worker.availableId += 1


        #is it necessary?
        #self.notEnoughHours = False

        #schedule that worker will actually work
        self.schedule = []

        #requested schedule - created by AvalRules
        self.rqSchedule = [] #

        self.rules = []

        

    def serializer(self):

        #we don't need to save schedules, just rules

        return{
            "__type__": "Worker",
            "name": self.name,
            "surname": self.surname,
            "pesel":self.pesel,
            "id":self.id,
            #"schedule": [shift.serializer() for shift in self.schedule],
            #serializer for every rule
            "rules":[rule.serializer() for rule in self.rules],
            #"rqSchedule":[shift.serializer() for shift in self.rqSchedule]
            
        }


    def addRequestedSchedule(self, rqSchedule):

        #check if all shifts of worker calendar are ShiftPlace   

        if isinstance(rqSchedule, list) and all(isinstance(s, ShiftPlace) for s in rqSchedule):
            self.rqSchedule = rqSchedule

    def availableToday(self, date):
        for shift in self.rqSchedule:
             if shift.begin.date() >= date and shift.end.date() <= date:
                    return True
        return False

    #checks every rule or rules of given class
    def compliesRules(self, shift, rule_class=None):
        import rules
        
        #RightRules - every one of them needs to be fulfilled at the same time
        worker_rules = [r for r in self.rules if isinstance(r, rules.RightRule)]
        for rule in worker_rules:
            if not rule.isFulfilled(shift):
                return False
                
       #availability rules - at least one of them needs to be fulfilled
        availability_rules = [r for r in self.rules if isinstance(r, rules.AvalRule)]
        if availability_rules:
            passed_any = False
            for rule in availability_rules:
                if rule.isFulfilled(shift):
                    passed_any = True
                    break
            
            if not passed_any:
                return False
                
        return True
    
    def addAcqShift(self, shift):
        self.acquiredSchedule.append(shift)

    def addRule(self, rule):
        self.rules.append(rule)


    def removeRule(self, ruleId):
        for rule in self.rules:
            if rule.id == ruleId:
                self.rules.remove(rule)
                return True
        return False

    #return first etat rule or None if there is no such rule
    def getEtatRule(self):
        for rule in self.rules:
            if isinstance(rule, EtatRule):
                return rule
        

    def howManyHours(self):

        workingTime = timedelta(0)
        for shift in self.acquiredSchedule:
            workingTime += shift.duration()
        return workingTime
        


    """
    #don't see point of this method    
    #how many hours maximum with rules it could work    
    def availability(self):

        #every place multiplies availability
        #we count hours not shifts!?!?!?
        maxHours = 0

        for i in range(len(self.rqSchedule)):
            #we take sum of shifts which do not overlap

            #NEED TO CHECK RULES FOR THESE SHIFTS!!!!!
            

            #availability = all hours, even if shifts overlap

            shiftCombinations = list(combinations(self.rqSchedule), i)

            #checking if combinations comly with rules

            if(self.complyWithRules(shiftCombinations)==1):
                if(utils.hoursSum(shiftCombinations) > maxHours):
                    maxHours = utils.hoursSum(shiftCombinations)

        return maxHours
    """


