
#cyclic = every: day, month, year

from abc import ABC, abstractmethod
from shift import ShiftPlace

from datetime import datetime, timedelta
from worker import Worker
from place import Place
from copy import deepcopy

#there are different types of rules
#rules of days worker is available - only one rule needs to be fulfilled in order to accept this shift

#rules deciding quality of work - break between work and so on

#RULES FOR availability
class AvalRule(ABC):

    idBase = 0

    def __init__(self, name):
        self.id = AvalRule.idBase
        AvalRule.idBase+=1
        self.type_name = "basic"
        self.name = name

    
    #returns ture or false
    @abstractmethod
    def isFulfilled(self, shift):
        if not (isinstance(shift, ShiftPlace)):
            return False
        else:
            True
    

    #returns shifts which cause conflict with the rule
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
class UnorderedRule(AvalRule):
    def __init__(self, shiftList, name):
        super().__init__(name)

        #is it necessary? - type_name_unrodered
       # self.type_name = "unordered"
        if not(isinstance(shiftList, list) and all(isinstance(item, ShiftPlace) for item in shiftList)):
            return None #is there exception

        self.shiftList = shiftList
        
    #if this shift is in a day, which is as the list
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
                return None #when this shift is complies with rules
           
           if isinstance(shift, list ) and all(isinstance(item, ShiftPlace) for item in shift):
                issue_shifts = []
                for elem in shift:
                    for item in self.shiftList:
                        if (item != shift):
                            issue_shifts.append(elem)
                return issue_shifts #when this shift is complies with rules

class CyclicRule(AvalRule):

    def __init__(self, begin, interval, name):
        super().__init__(name)
        if not (isinstance(begin, ShiftPlace)):
            raise TypeError("Parametr 'begin' musi być instancją ShiftPlace")
        
        #self.type_name = "cyclic"
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
           # tested_place = getattr(shift.place, 'name', shift.place)
            #cyclic_place = getattr(self.begin.place, 'name', self.begin.place)
            
            if shift.place == self.begin.place:
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
class RightRule(ABC):
    idBase = 0

    def __init__(self, owner, name):
        
        self.id = RightRule.idBase
        RightRule.idBase+=1
        
        self.type_name = "basic worker"

        #worker or place which has this rule
        self.owner = owner
        self.name = name
    
    @abstractmethod
    def isFulfilled(self, shift):
        pass

    @abstractmethod
    def serializer(self):
        pass


#how many hours max he can work
class EtatRule(RightRule):
    #name not available for user to change
    def __init__(self, owner, name, value, deviation):
        super().__init__(owner, name)
      
        if not isinstance(value, timedelta) or not isinstance(deviation, timedelta):
            raise TypeError("Parametry 'value' oraz 'deviation' muszą być obiektami typu timedelta")
    
        #self.type_name = "etat"
        self.name = name
        self.value = value
        self.deviation = deviation 

    #checks only if there isn't too much work

    #not too less
    def isFulfilled(self, shift):

        hoursWorked = timedelta(0)

        for shift in self.owner.acquiredSchedule:
            hoursWorked += shift.duration()

        hoursWorked += shift.duration()

        if hoursWorked >= (self.value - self.deviation) and  hoursWorked <= (self.value + self.deviation):
            return (True, self.value - hoursWorked)
        
        return (False, self.value - hoursWorked)

        #old version without checking minimum hours
        
        if hoursWorked <= self.value + self.deviation:
            #return (True, self.value - hoursWorked)
            return True
        #return (False, self.value - hoursWorked)  
        return False  
    
    """
    #useless function - fulfill does everything
    #if minimum hours he got
    def isComplete(self):
        hoursWorked = timedelta(0)

        for shift in self.owner.acquiredSchedule:
            hoursWorked += shift.duration()

        hoursWorked += shift.duration()

       # if hoursWorked >= (self.value - self.deviation) and  hoursWorked <= (self.value + self.deviation):
        #    return (True, self.value - hoursWorked)
        #return (False, self.value - hoursWorked)

        if hoursWorked >= self.value - self.deviation:
          
            return True
     
        return False  
    
    """

    
    
    def serializer(self):
        return{
            "__type__": "Etat Rule",
            "id": self.id,
            "owner": self.owner.id if hasattr(self, 'owner') else None, #when this rule is used for place
            "name": self.name,
            "value": self.value,
            "deviation": self.deviation

        }

#doesn't check weekends on the edge of months
class FreeWeekend(RightRule):

    def __init__(self, owner, name, quantity = 2):
        super().__init__(owner, name)
      
        #self.type_name = "free weekends"
        self.name = name
        self.quantity = quantity

    def isFulfilled(self, _, checkedMonth):

        emptyWeekend = 0
        #we check iof whole weekend is empty

        if not isinstance(checkedMonth, int) or 1 <= checkedMonth <= 12:
            raise ValueError("Parametr 'checkedMonth' musi być liczbą całkowitą z zakresu 1-12")

        #we check every weekend in the month

        pointer = datetime.today() 

        # 2. Use .replace() to create a new object with the desired month and day=1
        pointer = pointer.replace(month=checkedMonth, day=1)

        while(pointer.strftime("%A") != "Saturday"):
            pointer += timedelta(days=1)

        while(pointer.month == checkedMonth):
            
            if pointer.strftime("%A") != "Saturday":
                pointer += timedelta(days=1)
                if pointer.strftime("%A") != "Sunday":
                    emptyWeekend+=1


        if emptyWeekend >= self.quantity:
            return True
        
        return False
    
    def serializer(self):
        return{
            "__type__": "FreeWeekend",
            "id": self.id,
            "worker": self.worker.id if hasattr(self, 'worker') else None, #when this rule is used for place
            "name": self.name
        }
        



class BetweenShifts(RightRule):
    def __init__(self, place, name):
       
        super().__init__(place, name)
        #self.type_name = "between shifts"

    #to do 
    def isFulfilled(self, shift):
        pass     
    
    def serializer(self):
        return {
            "__type__": "BetweenShifts",
            "id": self.id,
            "place": getattr(self.place, 'id', self.place),
            "name": self.name
        }


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
        
        new_rule = CyclicRule(begin_shift, interval, rule_name, Worker)
    
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