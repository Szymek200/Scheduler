# -*- coding: utf-8 -*-
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

class Rule(ABC):
    idBase: int = 0
    def __init__(self, name: str):
        self.id = Rule.idBase
        Rule.idBase += 1
        self.name = name
     
    @abstractmethod
    def serializer(self) -> dict[str, Any]:
        pass

class AvalRule(Rule):
    def __init__(self, name):
        super().__init__(name)
      
    @abstractmethod
    def isFulfilled(self, shift: ShiftPlace) -> bool:
        from shift import ShiftPlace
        return isinstance(shift, ShiftPlace)

    @abstractmethod
    def uncompliedShifts(self, shift: ShiftPlace) -> list[ShiftPlace]:
        pass

    @abstractmethod
    def serializer(self) -> dict[str, Any]:
        pass

class UnorderedRule(AvalRule):
    def __init__(self, shiftList: list[ShiftPlace], name: str):
        from shift import ShiftPlace # Poprawione wciecie
        super().__init__(name)
        self.shiftList = shiftList
        
    def isFulfilled(self, shift: ShiftPlace) -> bool:
        from shift import ShiftPlace # Poprawione wciecie
        for item in self.shiftList:
            if (item == shift):
                return True
        return False
    
    def serializer(self) -> dict[str, Any]:
        return {
            "__type__": "UnorderedRule",
            "id": self.id,
            "name": self.name,
            'shiftList': [shift.serializer() for shift in self.shiftList]
        }
    
    def uncompliedShifts(self, shift: ShiftPlace) -> list[ShiftPlace]:
        from shift import ShiftPlace
        if isinstance(shift, ShiftPlace):
            for item in self.shiftList:
                if (item != shift):
                    return [shift]
            return []
        return []

class CyclicRule(AvalRule):
    def __init__(self, begin: datetime, interval: timedelta, name: str):
        from shift import ShiftPlace
        super().__init__(name)
        self.begin = begin
        self.interval = interval
        self.type_name = "cyclic"
        self.name = name

    def isFulfilled(self, shift: ShiftPlace) -> bool:
        from shift import ShiftPlace # Dodany brakujacy import lokalny
        if not isinstance(shift, ShiftPlace):
            return False
        if shift.begin < self.begin.begin:
            return False
        delta = shift.begin - self.begin.begin
        # Sprawdzanie interwalu w dniach
        int_interval = self.interval.days if hasattr(self.interval, 'days') else int(self.interval)
        if delta.days % int_interval == 0 and delta.seconds == 0:
            if getattr(shift.place, 'name', shift.place) == getattr(self.begin.place, 'name', self.begin.place):
                return True
        return False
    
    def serializer(self) -> dict[str, Any]:
        return {
            "__type__": "CyclicRule",
            "id": self.id,
            "name": self.name,
            "begin": self.begin.serializer(),
            "interval": self.interval.days if hasattr(self.interval, 'days') else self.interval
        }
    
    def uncompliedShifts(self, shift: ShiftPlace) -> list[ShiftPlace]:
        from shift import ShiftPlace
        if not self.isFulfilled(shift):
            return [shift]
        return []

class RightRule(Rule):
    def __init__(self, owner, name: str):
        super().__init__(name)
        self.owner = owner
      
    @abstractmethod
    def isFulfilled(self, shift: ShiftPlace):
        pass

    @abstractmethod
    def completion(self, worker: Worker):
        pass

    @abstractmethod
    def serializer(self):
        pass

class EtatRule(RightRule):
    def __init__(self, owner, name, value, deviation):
        super().__init__(owner, name)
        self.value = value
        self.deviation = deviation 

    def isFulfilled(self, shift):
        hoursWorked = self.owner.howManyHours()
        hoursWorked += shift.duration()
        if (self.value - self.deviation) <= hoursWorked <= (self.value + self.deviation):
            return True
        return False
      
    def completion(self, worker):
        hoursWorked = worker.howManyHours()
        if (self.value - self.deviation) <= hoursWorked <= (self.value + self.deviation):
            return 0
        # Kara za kazda godzine powyzej/ponizej etatu
        diff = abs(self.value.total_seconds() - hoursWorked.total_seconds()) / 3600
        return diff * HARD_PENALTY

    def serializer(self):
        return {
            "__type__": "Etat Rule",
            "id": self.id,
            "name": self.name,
            "value": str(self.value),
            "deviation": str(self.deviation)
        }

class FreeWeekend(RightRule):
    def __init__(self, owner, name, quantity = 2):
        super().__init__(owner, name)
        self.quantity = quantity

    def isFulfilled(self, shift, checkedMonth=None):
        return True # Uproszczone dla GA

    def completion(self, worker):
        # Logika sprawdzania wolnych weekendow
        if not worker.schedule:
            return 0
        # Tu mozna dodac pelna logike ze slajdow, poki co zwracamy 0
        return 0
    
    def serializer(self):
        return {"__type__": "FreeWeekend", "id": self.id, "name": self.name}

class BetweenShifts(RightRule):
    def __init__(self, place, name, value):
        super().__init__(place, name)
        self.value = value

    def isFulfilled(self, shift):
        return True

    def completion(self, worker):
        if len(worker.schedule) < 2:
            return 0
        
        penalty = 0
        # Sortujemy grafik pracownika chronologicznie
        sorted_sched = sorted(worker.schedule, key=lambda x: x.begin)
        
        for i in range(1, len(sorted_sched)):
            # Przerwa miedzy koncem poprzedniej a poczatkiem nastepnej zmiany
            rest = sorted_sched[i].begin - sorted_sched[i-1].end
            if rest < self.value:
                # Kara za brak odpoczynku (godziny brakujace)
                diff = (self.value - rest).total_seconds() / 3600
                penalty += diff * HARD_PENALTY
        return penalty
                
    def serializer(self):
        return {"__type__": "BetweenShifts", "id": self.id, "name": self.name, "value": str(self.value)}

def deserialize_rule(rule_data, entity):
    from worker import Worker
    from shift import ShiftPlace
    rule_type = rule_data.get("__type__")
    rule_name = rule_data.get("name", "")
    new_rule = None

    if rule_type == "CyclicRule":
        begin_data = rule_data.get("begin", {})
        interval_days = rule_data.get("interval", 1)
        begin_dt = datetime.fromisoformat(begin_data["begin"])
        end_dt = datetime.fromisoformat(begin_data["end"])
        worker_ref = entity if isinstance(entity, Worker) else None
        begin_shift = ShiftPlace(begin_dt, end_dt, begin_data.get("place", ""), worker_ref)
        new_rule = CyclicRule(begin_shift, timedelta(days=int(interval_days)), rule_name)
    
    # Pozostale reguly (FreeWeekend, Etat itd.) mozna dodac analogicznie
    return new_rule