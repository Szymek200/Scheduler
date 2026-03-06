
from calendar import Calendar
from datetime import datetime, time, timedelta
from itertools import combinations


import utils

from shift import ShiftPlace

class Worker:

    #class variable

    availableId = 1


    def __init__(self, name, surname, pesel, etat):
        self.name = name
        self.surname = surname
        self.pesel = pesel

        self.id = self.availableId
        Worker.availableId += 1

        self.notEnoughHours = False
        self.etat = etat

        #schedule that worker will actually work
        self.acquiredSchedule = []

        #requested schedule
        self.rqSchedule = [] #

        self.rules = []

        

    def serializer(self):
        return{
            "__type__": "Worker",
            "name": self.name,
            "surname": self.surname,
            "pesel":self.pesel,
            "id":self.id,
            "acquiredSchedule": [shift.serializer() for shift in self.acquiredSchedule],
            #serializer for every rule
            "rules":[rule.serializer() for rule in self.rules],
            "etat": self.etat,
            "rqSchedule":[shift.serializer() for shift in self.rqSchedule]
            
        }
       

    def addRequestedSchedule(self, rqSchedule):

            #check if all shifts of worker calendar are ShiftPlace
        if isinstance(rqSchedule, Calendar) and all(isinstance(s, ShiftPlace) for s in rqSchedule.shiftList):
            self.rqSchedule = rqSchedule

    def worksToday(self, date):
        for shift in self.rqSchedule:
             if shift.begin.date == date or shift.end.date:
                    return True
        return False

    #different alrguments for rules
    def compliesRules(self, shift, rule_class=None):
        for rule in self.rules:
            # Jeśli podaliśmy klasę bazową, sprawdzamy czy reguła po niej dziedziczy.
            # Jeśli nie, pomijamy ją i idziemy do następnej w pętli.
            if rule_class is not None and not isinstance(rule, rule_class):
                continue
            
            # Sprawdzamy czy reguła jest spełniona
            # (Uwaga: upewnij się, czy w danym przypadku isFulfilled wymaga 'shift' czy nie)
            if not rule.isFulfilled(shift):
                return False
                
        return True 
    

    def compliesRulesRequest(self, shift, rule_class=None):
        import rules # Import wewnątrz, żeby uniknąć problemów
        
        # Zbieramy reguły do sprawdzenia
        rules_to_check = [r for r in self.rules if rule_class is None or isinstance(r, rule_class)]
        
        # Jeśli pracownik nie ma żadnych reguł, zależy to od Twojej logiki biznesowej.
        # Obecnie zakładamy, że jeśli nie ma reguł, to nie ma zdefiniowanej dostępności.
        if not rules_to_check:
            return False
            
        # 1. Logika dla reguł dostępności (CyclicRule, UnorderedRule)
        # Zmiana musi pasować do PRZYNAJMNIEJ JEDNEJ reguły (logika OR)
        if rule_class == rules.Rule:
            for rule in rules_to_check:
                if rule.isFulfilled(shift):
                    return True # Wystarczy jedna pasująca reguła!
            return False
            
        # 2. Logika dla innych reguł (np. odpoczynek - WorkerRule)
        # Zmiana musi spełniać WSZYSTKIE reguły tego typu (logika AND)
        for rule in rules_to_check:
            if not rule.isFulfilled(shift):
                return False
                
        return True
    
    def addWorkerShift(self, shift):
        self.acquiredSchedule.append(shift)

    def addRule(self, rule):
        self.rules.append(rule)

    def howManyHours(self):

        workingTime = timedelta(0)
        for shift in self.acquiredSchedule:
            workingTime += shift.duration()
        return workingTime
        
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



