
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
        self.availableId += 1

        self.notEnoughHours = False
        self.etat = etat

        #schedule that worker will actually work
        self.acquiredSchedule = []

        self.rules = []

        

       
   
        
            

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
    def compliesRules(self, shift):
        for rule in self.rules:
            if not rule.isFulfilled():
                return False
        return True   
    
    def addWorkerShift(self, shift):
        self.acquiredSchedule.append(shift)

    def addRule(self, rule):
        self.rules.append(rule)

    def howManyHours(self):

        workingTime = timedelta(0)
        for shift in self.acquiredSchedule:
            timedelta += shift.duration()
        return workingTime
        
    #how many hours maximum with rules it could work    
    def availability(self):

        #every place multiplies availability
        #we count hours not shifts!?!?!?

        for i in range(len(self.rqSchedule)):
            #we take sum of shifts which do not overlap

            #NEED TO CHECK RULES FOR THESE SHIFTS!!!!!
            maxHours = 0

            #availability = all hours, even if shifts overlap

            shiftCombinations = list(combinations(self.rqSchedule), i)

            #checking if combinations comly with rules

            if(self.complyWithRules(shiftCombinations)==1):
                if(utils.hoursSum(shiftCombinations) > maxHours):
                    maxHours = utils.hoursSum(shiftCombinations)



