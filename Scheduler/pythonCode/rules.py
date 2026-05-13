
#cyclic = every: day, month, year

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from copy import deepcopy
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from shift import ShiftPlace
    from worker import Worker
    from place import Place

from constans import HARD_PENALTY, SOFT_PENALTY

#there are different types of rules
#rules of days worker is available - only one rule needs to be fulfilled in order to accept this shift

#rules deciding quality of work - break between work and so on

class Rule(ABC):
    idBase: int = 0

    def __init__(self, name: str):
        self.id = Rule.idBase
        Rule.idBase+=1
        self.name = name
     
    @abstractmethod
    def serializer(self) -> dict[str, Any]:
        pass


#RULES FOR availability
class AvalRule(Rule):



    def __init__(self, name):
        super().__init__(name)
      
    #returns ture or false
    @abstractmethod
    def isFulfilled(self, shift:ShiftPlace) -> bool:
        if not (isinstance(shift, ShiftPlace)):
            return False
        else:
            return True
    

    #returns shifts which cause conflict with the rule
    @abstractmethod
    def uncompliedShifts(self, shift: ShiftPlace) -> list[ShiftPlace]:
        pass

    @abstractmethod
    def serializer(self) -> dict[str, Any]:
        pass

    #returns required form options to create this rule
        
#rules for requested Schedule

#only in particular days it can work

#RULE - can worker or place is available
#only for schedule purpose
class UnorderedRule(AvalRule):
    def __init__(self, shiftList:  list[ShiftPlace], name: str):
        super().__init__(name)

        #is it necessary? - type_name_unrodered
       # self.type_name = "unordered"
        if not(isinstance(shiftList, list) and all(isinstance(item, ShiftPlace) for item in shiftList)):
            return None #is there exception

        self.shiftList = shiftList
        
    #if this shift is in a day, which is as the list
    def isFulfilled(self, shift:ShiftPlace) -> bool:
        for item in self.shiftList:
            if (item == shift):
                return True

        return False
    
    def serializer(self) -> dict[str, Any]:
        return{
            "__type__": "UnorderedRule",
            "id": self.id,
            "name": self.name,
            'shiftList': [shift.serializer() for shift in self.shiftList]
        }
    
    #shifts which cause conflict
    def uncompliedShifts(self, shift: ShiftPlace) -> list[ShiftPlace]:
           
         
           if isinstance(shift, ShiftPlace):
                for item in self.shiftList:
                    if (item != shift):
                        #this shift does not comply with the rule
                        return [shift] #one element list
                return [] #when this shift is complies with rules
           
           if isinstance(shift, list ) and all(isinstance(item, ShiftPlace) for item in shift):
                issue_shifts: list[ShiftPlace] = []
                for elem in shift:
                    for item in self.shiftList:
                        if (item != shift):
                            issue_shifts.append(elem)
                return issue_shifts #when this shift is complies with rules

class CyclicRule(AvalRule):

    def __init__(self, begin: datetime, interval: timedelta, name: str):
        from shift import ShiftPlace
        super().__init__(name)
        if not (isinstance(begin, ShiftPlace)):
            raise TypeError("Parametr 'begin' musi być instancją ShiftPlace")
        
   
        self.begin = begin
        self.interval = interval
        self.name = name

    def isFulfilled(self, shift: ShiftPlace) -> bool:
       
        if not isinstance(shift, ShiftPlace):
            return False

        #checked shift must be after original shift in rule
        if shift.begin < self.begin.begin:
            return False
            
        #difference between shifts
        delta = shift.begin - self.begin.begin
        
       
        if delta.days % self.interval.days == 0 and delta.seconds == 0:
            if shift.place == self.begin.place:
                return True
                    
        return False
    
    def serializer(self) -> dict[str, Any]:
        return{
            "__type__": "CyclicRule",
            "id": self.id,
            "name": self.name,
            "begin": self.begin.serializer(),
            "interval": self.interval
        }
    
    #check which shifts cause conflicts
    def uncompliedShifts(self, shift: ShiftPlace) -> list[ShiftPlace]:
       
        if isinstance(shift, ShiftPlace):
            if not self.isFulfilled(shift):
                return [shift]  
            return []    
            
        # Jeśli przekazano LISTĘ zmian
        elif isinstance(shift, list) and all(isinstance(item, ShiftPlace) for item in shift):
            issue_shifts = []
            for item in shift:
                if not self.isFulfilled(item):
                    issue_shifts.append(item)
            return issue_shifts #returns shifts which cause conflict
            
        return []

    

#WORKER RULE
#for worker and place rights
class RightRule(Rule):
  

    def __init__(self, owner, name: str):
        super(name)
        #worker or place which has this rule
        self.owner = owner
      
    
    @abstractmethod
    def isFulfilled(self, shift: ShiftPlace):
        pass

    #plus value is wrong - penalty for genetic alg
    @abstractmethod
    def completion(self, worker: Worker):
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

        for shift in self.owner.schedule:
            hoursWorked += shift.duration()

        hoursWorked += shift.duration()

        if hoursWorked >= (self.value - self.deviation) and  hoursWorked <= (self.value + self.deviation):
            return (True, self.value - hoursWorked)
        
        return (False, self.value - hoursWorked)

      
    def completion(self, worker):

        hoursWorked = timedelta(0)

        for shift in self.owner.schedule:
            hoursWorked += shift.duration()

        hoursWorked += shift.duration()
       
        if hoursWorked >= (self.value - self.deviation) and  hoursWorked <= (self.value + self.deviation):
            #return (True, self.value - hoursWorked)

            #not enough work
            if self.value - hoursWorked > 0:
              return (self.value - self.deviation - hoursWorked)* SOFT_PENALTY
            else:
                return (self.value + self.deviation - hoursWorked)* SOFT_PENALTY
        
       # return (False, self.value - hoursWorked)

        return (self.value - hoursWorked).total_seconds // 3600  * HARD_PENALTY


    
    
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
    
    #returns how many working hours has worker in the month
    def completion(self, worker):

        emptyWeekend = 0

        weekendWorkingHours = timedelta(0)
        #we check if whole weekend is empty

        #we check every weekend in the month

        if not worker.schedule[0]:
            return 0    #zero working hours in the weekend
            
        #what if first shift is in before month? - be take ending of the shift
        pointer = worker.schedule[0].begin

        pointer = pointer.replace(day=1)

        current_month = pointer.month

        #month starts with sunday
        if pointer.weekday() == 6:
            response =worker.worksToday(pointer)
            if response:
                for shift in response:
                    weekendWorkingHours += shift.duration()
            else:
                emptyWeekend+=1

        while pointer.month == current_month:
        # 5 Sobota, 6 Niedziela
            if pointer.weekday() == 5:
                 saturday =worker.worksToday(pointer)
                

                 pointer += timedelta(days=1)
                 if(pointer.month == current_month):
                    sunday =worker.worksToday(pointer)

                 if saturday or sunday:
                    for shift in saturday, sunday:
                        weekendWorkingHours += shift.duration()
                 else:
                     emptyWeekend+=1;
     
            pointer += timedelta(days=5)  # Przejdź do następnej soboty

        #how many weekends occupied - minus - wrong, zero and plus - good
        #whole weekend working hours - can't determine which weekend is ok and which is not

        #return (self.quantity - emptyWeekend, weekendWorkingHours)

        if self.quantity <= emptyWeekend:
            return 0
        else:
            return weekendWorkingHours.total_seconds //3600 * HARD_PENALTY


    
    def serializer(self):
        return{
            "__type__": "FreeWeekend",
            "id": self.id,
            "worker": self.worker.id if hasattr(self, 'worker') else None, #when this rule is used for place
            "name": self.name
        }
        



class BetweenShifts(RightRule):
    def __init__(self, place, name, value):
       
        super().__init__(place, name)
        self.value = value
        #self.type_name = "between shifts"

    #to do 
    def isFulfilled(self, worker):


        for i in range(len(worker.shedule)): 

            if i == 0:
                continue
            if worker.shedule[i].begin - worker.shedule[i-1].end < self.value:
                return False


    def completion(self, worker):

        #value - timedelta between shifts
        overlapHours = timedelta(0)

        for i in range(len(worker.shedule)): 

            if i == 0:
                continue

            delta = worker.shedule[i].begin - worker.shedule[i-1].end < self.value
            delta -= self.value
            if delta > 0:
                overlapHours += delta

        return delta.total_seconds //3600 * HARD_PENALTY
                
        
    
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

    from worker import Worker
    from shift import ShiftPlace

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