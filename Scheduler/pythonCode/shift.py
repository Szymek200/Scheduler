from __future__ import annotations
from datetime import datetime, time, timedelta
import json


from typing import Any, Self, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from place import Place
    from worker import Worker


class Shift:

    #many times can be used
    #datetime - specific date
    #or just time 
    def __init__(self, begin:datetime, end:datetime):
            
            self.begin: datetime = begin
            self.end: datetime = end
        
        
    def duration(self)-> timedelta:
        return self.end - self.begin
    
    #__eq needs work with Any Object
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Shift):
            return False
        if self.begin == other.end and self.end == other.end:
            return True
        
        return False
    
    #shifts are equal or an argument fit inside hours of this shift
    def contains(self, shift: Shift) -> bool:

        if isinstance(shift, Shift):

            if self.begin <= shift.begin and self.end >= shift.end:
                return True
            
        return False
    
    def serializer(self) -> dict[str, Any]:
        return{
            "__type__": "Shift",
            "begin": self.begin,
            "end": self.end
        }
    
    #something like static class
    #requires cls object - something similar to self in methods for objects

    #@staticmethod doesn't have cls, so it needs already existing object to work on
    @classmethod
    def deserializer(cls, json_string: str) -> Self: #Self - funkcja zwraca typ klasy, na rzecz ktorej zostala wywolana
        #translate json file into data structure we understand
        data = json.loads(json_string)

        begin = datetime.fromisoformat(data["begin"])
        end = datetime.fromisoformat(data["begin"])

        return cls(begin, end)
    
        
# place shouldn't be set but just one particular object
class ShiftPlace(Shift):
    def __init__(self, begin: datetime, end: datetime, place: Place | str, worker: Optional[Worker | int] = None):
        super().__init__(begin, end)
        self.place = place
        self.worker = worker

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ShiftPlace):
            return False
        
        # Bezpieczne porównanie miejsc (jako obiekty lub stringi)
        self_p = getattr(self.place, 'name', self.place)
        other_p = getattr(other.place, 'name', other.place)
        
        if self.begin == other.begin and self.end == other.end:
            if self_p == other_p:
                return True
        return False
    
    def contains(self, shift: Shift) -> bool:
        if super().contains(shift):   
            self_p = getattr(self.place, 'name', self.place)
            other_p = getattr(shift, 'place', None)
            if hasattr(shift, 'place'):
                other_p = getattr(shift.place, 'name', shift.place)
            if self_p == other_p:
                return True 
        return False

    def sameShift(self, shift: ShiftPlace) -> bool:
        if self.__eq__(shift):
            self_w = getattr(self.worker, 'id', self.worker)
            other_w = getattr(shift.worker, 'id', shift.worker)
            if self_w == other_w:
                return True
        return False
        
    def serializer(self) -> dict[str, Any]:
        # Gwarancja pobrania wyłącznie czystych ID/Nazw do pliku JSON
        place_id = getattr(self.place, 'name', self.place)
        worker_id = getattr(self.worker, 'id', self.worker) if self.worker is not None else None

        return {
            "__type__": "ShiftPlace",
            "begin": self.begin.isoformat(),
            "end": self.end.isoformat(),
            "place": place_id,
            "worker": worker_id
        }
    
    @classmethod
    def deserializer(cls, json_string: str) -> Self:
        data = json.loads(json_string)
        
        begin = datetime.fromisoformat(data["begin"])
        end = datetime.fromisoformat(data["end"])
        
        # Zwracamy tymczasowo z surowymi ID. saving.py podmieni je na obiekty.
        place = data["place"]
        worker = data.get("worker")
        
        return cls(begin, end, place, worker)


