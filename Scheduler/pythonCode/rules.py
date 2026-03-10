
#cyclic = every: day, month, year

from abc import ABC, abstractmethod
from shift import Shift, ShiftPlace

from datetime import datetime, time, timedelta, date
from worker import Worker
from place import Place
from copy import deepcopy

#there are different types of rules
#rules of days worker is available - worker rules

#rules deciding quality of work - break between work and so on

#RULES FOR availability
class Rule(ABC):

    idBase = 0

    def __init__(self, name, owner):
        self.id = Rule.idBase
        Rule.idBase+=1
        self.type_name = "basic"
        self.name = name
        self.owner = owner
    
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

    @abstractmethod
    def serializer(self):
        pass

    #returns required form options to create this rule
        
#rules for requested Schedule

#only in particular days it can work

#RULE - can worker or place is available
#only for schedule purpose
class UnorderedRule(Rule):
    def __init__(self, shiftList, name):
        super().__init__(name)
        self.type_name = "unordered"
        if not(isinstance(shiftList, list) and all(isinstance(item, ShiftPlace) for item in shiftList)):
            return None #is there exception

        self.shiftList = shiftList
        
    
    def isFulfilled(self, shift):
        for item in self.shiftList:
            if (item == shift):
                return True

        return False
    
    def serializer(self):
        return{
            "__type__": "UnorderedRule",
            "id": self.id,
            "name": self.name,
            'shiftList': [shift.serializer() for shift in self.shiftList]
        }
    
    #shifts which cause conflict
    def uncompliedShifts(self, shift):
           
         
           if isinstance(shift, ShiftPlace):
                for item in self.shiftList:
                    if (item != shift):
                        #this shift does not comply with the rule
                        return shift
                return #when this shift is complies with rules
           
           if isinstance(shift, list ) and all(isinstance(item, ShiftPlace) for item in shift):
                issue_shifts = []
                for elem in shift:
                    for item in self.shiftList:
                        if (item != shift):
                            issue_shifts.append(elem)
                return issue_shifts #when this shift is complies with rules

        
    




class CyclicRule(Rule):

    def __init__(self, begin, interval, name):
        super().__init__(name)
        if not (isinstance(begin, ShiftPlace)):
            raise TypeError("Parametr 'begin' musi być instancją ShiftPlace")
        
        self.type_name = "cyclic"
        self.begin = begin
        self.interval = interval
        self.name = name

    def isFulfilled(self, shift):
       
        if not isinstance(shift, ShiftPlace):
            return False

        #checked shift must be after original shift in rule
        if shift.begin < self.begin.begin:
            return False
            
        #difference between shifts
        delta = shift.begin - self.begin.begin
        
       
        if delta.days % self.interval == 0 and delta.seconds == 0:
            
            #check place
            miejsce_badane = getattr(shift.place, 'name', shift.place)
            miejsce_cyklu = getattr(self.begin.place, 'name', self.begin.place)
            
            if miejsce_badane == miejsce_cyklu:
                return True
                    
        return False
    
    def serializer(self):
        return{
            "__type__": "CyclicRule",
            "id": self.id,
            "name": self.name,
            "begin": self.begin.serializer(),
            "interval": self.interval
        }
    
    #check which shifts cause conflicts
    def uncompliedShifts(self, shift):
       
        if isinstance(shift, ShiftPlace):
            if not self.isFulfilled(shift):
                return shift  
            return None      
            
        # Jeśli przekazano LISTĘ zmian
        elif isinstance(shift, list) and all(isinstance(item, ShiftPlace) for item in shift):
            issue_shifts = []
            for item in shift:
                if not self.isFulfilled(item):
                    issue_shifts.append(item)
            return issue_shifts #returns shifts which cause conflict
            
        return None

    

#WORKER RULE
#for worker and place rights
class WorkerRule(ABC):
    idBase = 0

    def __init__(self, worker, name):
        
        self.id = WorkerRule.idBase
        WorkerRule.idBase+=1

        if not (isinstance(worker, Worker)):
            return
        
        self.type_name = "basic worker"
        self.worker = worker
        self.name = name
    
    @abstractmethod
    def isFulfilled(self, shift):
        pass

    @abstractmethod
    def serializer(self):
        pass


#how many hours max he can work
class EtatRule(WorkerRule):
    #name not available for user to change
    def __init__(self, worker, name, value, deviation):
        super().__init__(worker, name)
      
        self.type_name = "etat"
        self.name = "EtatRule"
        self.value = value
        self.deviation = deviation

    #checks only if there isn't too much work

    #not too less
    def isFulfilled(self, shift):

        hoursWorked = timedelta(0)

        for shift in self.worker.acquiredSchedule:
            hoursWorked += shift.duration()

        hoursWorked += shift.duration()

       # if hoursWorked >= (self.value - self.deviation) and  hoursWorked <= (self.value + self.deviation):
        #    return (True, self.value - hoursWorked)
        #return (False, self.value - hoursWorked)

        if hoursWorked <= self.value + self.deviation:
            #return (True, self.value - hoursWorked)
            return True
        #return (False, self.value - hoursWorked)  
        return False  
    
    #if minimum hours he got
    def isComplete(self):
        hoursWorked = timedelta(0)

        for shift in self.worker.acquiredSchedule:
            hoursWorked += shift.duration()

        hoursWorked += shift.duration()

       # if hoursWorked >= (self.value - self.deviation) and  hoursWorked <= (self.value + self.deviation):
        #    return (True, self.value - hoursWorked)
        #return (False, self.value - hoursWorked)

        if hoursWorked >= self.value - self.deviation:
          
            return True
     
        return False  
    
    

    
    
    def serializer(self):
        return{
            "__type__": "Etat Rule",
            "id": self.id,
            "worker": self.worker.id if hasattr(self, 'worker') else None, #when this rule is used for place
            "name": self.name,
            "value": self.value,
            "deviation": self.deviation

        }

#doesn't check weekends on the edge of months
class FreeWeekend(WorkerRule):

    def __init__(self, worker, name):
        super().__init__(worker, name)
      
        self.type_name = "free weekends"
        self.name = name

    def isFulfilled(self, _):

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
    
    def serializer(self):
        return{
            "__type__": "FreeWeekend",
            "id": self.id,
            "worker": self.worker.id if hasattr(self, 'worker') else None, #when this rule is used for place
            "name": self.name
        }


class BetweenShifts(WorkerRule):
    def __init__(self, worker, name):
        super().__init__(worker, name)
     
        self.type_name = "between shifts"

    def isFulfilled(self, shift):
        shiftcopy = deepcopy(self.worker.acquiredSchedule)
        shiftcopy.append(shift)
        shiftcopy.sort(key= lambda shift: shift.begin)
        for i in range(1, len(shiftcopy)):
            if self.worker.acquiredSchedule[i].begin - self.worker.acquiredSchedule[i-1].end < timedelta(hours = 11):
                return False
        return True
    
    def serializer(self):
        return{
            "__type__": "BetweenShifts",
            "id": self.id,
            "worker": self.worker.id if hasattr(self, 'worker') else None,
            "name": self.name
        }
            

        
        

class PlaceRule(ABC):
    idBase = 0

    def __init__(self, place, name):
        self.id = PlaceRule.idBase
        self.name = name
        PlaceRule.idBase+=1

        if not (isinstance(place, Place)):
            return None
        
        self.type_name = "basic place"
        self.place = place
    
    @abstractmethod
    def isFulfilled(self, _):
        pass

    @abstractmethod
    def serializer(self):
        pass




# Dodaj na samym końcu pliku rules.py

def deserialize_rule(rule_data, entity):
    """
    Deserialization for every rule
    """
    rule_type = rule_data.get("__type__")
    rule_name = rule_data.get("name", "")
    rule_id = rule_data.get("id")

    new_rule = None

   
    if rule_type == "FreeWeekend":
        new_rule = FreeWeekend(entity, rule_name)

    elif rule_type == "BetweenShifts":
        new_rule = BetweenShifts(entity, rule_name)

    elif rule_type == "UnorderedRule":
        shifts_array = []
        for s_data in rule_data.get("shiftList", []):
            try:
                begin_dt = datetime.fromisoformat(s_data["begin"])
                end_dt = datetime.fromisoformat(s_data["end"])
            except (ValueError, TypeError, KeyError):
                print(f"Błąd parsowania daty w UnorderedRule: {s_data}")
                continue
            
            # Jeśli entity to pracownik, przypisz go do zmiany. Jeśli miejsce - zostaw None
            worker_ref = entity if isinstance(entity, Worker) else None
            shift = ShiftPlace(begin_dt, end_dt, s_data.get("place", ""), worker_ref)
            shifts_array.append(shift)
            
        new_rule = UnorderedRule(shifts_array, rule_name)

    elif rule_type == "CyclicRule":

        #whole serialized shift
        begin_data = rule_data.get("begin", {})
        interval = rule_data.get("interval", 1)
        
        try:
            begin_dt = datetime.fromisoformat(begin_data["begin"])
            end_dt = datetime.fromisoformat(begin_data["end"])
        except (ValueError, TypeError, KeyError):
            print(f"Błąd parsowania daty w CyclicRule: {begin_data}")
            return None
        
        worker_ref = entity if isinstance(entity, Worker) else None
        begin_shift = ShiftPlace(begin_dt, end_dt, begin_data.get("place", ""), worker_ref)
        
        new_rule = CyclicRule(begin_shift, interval, rule_name)
    
    elif rule_type == "EtatRule":
        try:
            value = timedelta.fromisoformat(rule_data.get("value"))
            deviation = timedelta.fromisoformat(rule_data.get("deviation"))
        except (ValueError, TypeError, KeyError):
            print(f"Błąd parsowania czasu w CyclicRule: {begin_data}")
            return None
        
        worker_ref = entity if isinstance(entity, Worker) else None
        
        new_rule = EtatRule(worker_ref, rule_name, value, deviation)

    # Przywracanie ID, jeśli udało się stworzyć regułę
    if new_rule and rule_id is not None:
        new_rule.id = rule_id

    return new_rule