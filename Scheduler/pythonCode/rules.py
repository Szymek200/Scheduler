
#cyclic = every: day, month, year

from abc import ABC, abstractmethod
from shift import Shift, ShiftPlace

from datetime import datetime, time, timedelta, date
from worker import Worker
from place import Place

class Rule(ABC):

    idBase = 0

    def __init__(self, name):
        self.id = idBase
        idBase+=1
        self.type_name = "basic"
        self.name = ""
    
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
        pass

    #returns required form options to create this rule
        
#rules for requested Schedule

#only in particular days it can work
class UnorderedRule(Rule):
    def __init__(self, shiftList, name):
        super().__init__(name)
        self.type_name = "unordered"
        if not(isinstance(shiftList, list) and all(isinstance(item, ShiftPlace) for item in shiftList)):
            return 0 #is there exception

        self.shiftList = shiftList
        
    
    def isFulfilled(self, shift):
        for item in self.shiftList:
            if (item == shift):
                return True

        return False
    




class CyclicRule(Rule):

    def __init__(self, begin, interval, name):
        super().__init__(name)
        if not (isinstance(begin, ShiftPlace)):
            return 0 #exception would be better
        
        self.type_name = "cyclic"
        self.begin = begin
        self.interval = interval
        self.name = name

    def isFulfilled(self, shift):

        pointer = self.begin

        if(pointer == shift):
            return True
        


        while(pointer < shift):
        
            pointer += self.interval

            if(pointer == shift):
                return True
        

        return False
    


class WorkerRule(ABC):
    idBase = 0

    def __init__(self, worker, name):
        
        self.id = idBase
        idBase+=1

        if not (isinstance(worker, Worker)):
            return 0
        
        self.type_name = "basic worker"
        self.worker = worker
        self.name = name
    
    @abstractmethod
    def isFulfilled(self):
        pass


#doesn't check weekends on the edge of months
class FreeWeekend(WorkerRule):

    def __init__(self, worker, name):
        super().__init__(worker, name)
      
        self.type_name = "free weekends"
        self.name = name

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
    def __init__(self, worker, name):
        super().__init__(worker, name)
     
        self.type_name = "between shifts"

    def isFulfilled(self):

        
        for i in range(1, len(self.worker.acquiredSchedule)):
            if self.worker.acquiredSchedule[i].begin - self.worker.acquiredSchedule[i-1].end < timedelta(hours = 11):
                return False
        return True
            

        
        

class PlaceRule(ABC):
    idBase = 0

    def __init__(self, place, name):
        self.id = idBase
        self.name = name
        idBase+=1

        if not (isinstance(place, Place)):
            return 0
        
        self.type_name = "basic place"
        self.place = place
    
    @abstractmethod
    def isFulfilled(self):
        pass




