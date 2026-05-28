from __future__ import annotations
from datetime import datetime, timedelta
from abc import abstractmethod
from typing import TYPE_CHECKING, Any
from constans import HARD_PENALTY
from .Rule import Rule
from myExceptions import IntervalZero

if TYPE_CHECKING:
    from shift import ShiftPlace
    from worker import Worker


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

    def __init__(self, begin: ShiftPlace, interval: timedelta, name: str):
        from shift import ShiftPlace
        super().__init__(name)

        if interval == 0:
            raise IntervalZero("Interval is zero")
        self.begin = begin
        self.interval = interval
        self.type_name = "cyclic"
        self.name = name

    def isFulfilled(self, shift: ShiftPlace) -> bool:
        from shift import ShiftPlace 
        if not isinstance(shift, ShiftPlace):
            return False
        if shift.begin < self.begin.begin:
            return False
            
        delta = shift.begin - self.begin.begin
        
        # Pobieramy interwał w sekundach (skoro w serializerze dajesz total_seconds())
        if hasattr(self.interval, 'total_seconds'):
            int_interval_seconds = self.interval.total_seconds()
        else:
            # Zabezpieczenie: jeśli z JSON-a przyszedł float/int sekund
            int_interval_seconds = float(self.interval)
            
        # Jeśli dane w bazie były stare i były "dniami" (np. 1 lub 7 zamiast sekund), konwertujemy na sekundy
        if int_interval_seconds <= 1000:
            int_interval_seconds = int_interval_seconds * 24 * 3600

        # Sprawdzamy pełną zgodność co do sekundy
        if delta.total_seconds() % int_interval_seconds == 0:
            if getattr(shift.place, 'name', shift.place) == getattr(self.begin.place, 'name', self.begin.place):
                return True
        return False
    
    def serializer(self) -> dict[str, Any]:
        
        seconds_val = self.interval.total_seconds() if hasattr(self.interval, 'total_seconds') else float(self.interval)
        
        return {
            "__type__": "CyclicRule",
            "id": self.id,
            "name": self.name,
            "begin": self.begin.serializer(),
            "interval": seconds_val
        }
    
    def uncompliedShifts(self, shift: ShiftPlace) -> list[ShiftPlace]:
        from shift import ShiftPlace
        if not self.isFulfilled(shift):
            return [shift]
        return []
