
#cyclic = every: day, month, year

from abc import ABC, abstractmethod
import Shift
import ShiftPlace
from datetime import datetime, time, timedelta, date
import worker
import place

class Rule(ABC):

    idBase = 0

    def __init__(self):
        self.id = idBase
        idBase+=1
    
    @abstractmethod
    def isFulfilled(self, shift):
        if not (isinstance(shift, ShiftPlace)):
            return False
        else:
            True
    
    #to do -> implement it to all rules!!!!
    #returns shifts which cause conflict

    @abstractmethod
    def uncompliedShifts(self, shift):
        
#rules for requested Schedule

#only in particular days it can work
class UnorderedRule(Rule):

    def __init__(self, shiftList):
        super().__init__()

        if not(isinstance(shiftList, list) and all(isinstance(item, ShiftPlace) for item in shiftList)):
            return 0 #is there exception

        self.shiftList = shiftList
    
    def isFulfilled(self, shift):
        for item in self.shiftList:
            if (item == shift):
                return True

        return False

class CyclicRule(Rule):

    def __init__(self, begin, interval):
        
        if not (isinstance(begin, ShiftPlace)):
            return 0 #exception would be better
        
        self.begin = begin
        self.interval = interval

    def isFulfilled(self, shift):

        pointer = begin

        if(pointer == shift):
            return True
        


        while(pointer < shift):
        
            pointer += self.interval

            if(pointer == shift):
                return True
        

        return False

class WorkerRule(ABC):
    idBase = 0

    def __init__(self, worker):
        self.id = idBase
        idBase+=1

        if not (isinstance(worker, Worker)):
            return 0
        
        self.worker = worker
    
    @abstractmethod
    def isFulfilled(self):
        pass


#doesn't check weekends on the edge of months
class FreeWeekend(WorkerRuleRule):

    def __init__(self, worker):
        self.worker = worker

    def isFulfilled(self):

        emptyWeekend = 0
        #we check iof whole weekend is empty

        checkedMonth = self.shiftList.first.begin.month
        
        #we check every weekend in the month

        #can be just date
        pointer = datetime.today
        pointer.month = checkedMonth

        while(pointer.strftime("%A") != "Saturday"):
            pointer += timedelta(days=1)

        while(pointer.month == checkedMonth):
            
            if pointer.strftime("%A") != "Saturday":
                pointer += timedelta(days=1)
                if pointer.strftime("%A") != "Sunday":
                    emptyWeekend+=1
        
        return emptyWeekend


class BetweenShifts(WorkerRule):
    def __init__(self, worker):
        self.worker = worker

    def isFulfilled(self):

        
        for i in range(1, len(worker.acquiredSchedule)):
            if acquiredSchedule[i].begin - acquiredSchedule[i-1].end < timedelta(hours = 11):
                return False
        return True
            

        
        

class PlaceRule(ABC):
    idBase = 0

    def __init__(self, place):
        self.id = idBase
        idBase+=1

        if not (isinstance(place, Place)):
            return 0
        
        self.place = place
    
    @abstractmethod
    def isFulfilled(self):
        pass




