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
        dane = json.loads(json_string)

        return cls(begin = dane["begin"], end = dane["end"])
    
        
#place shouldn't be set but just one particular object
class ShiftPlace(Shift):
    # Zmiana: 'places' na 'place' (pojedynczy obiekt)
    def __init__(self, begin: datetime, end: datetime, place: Place, worker: Optional[Worker] =None):
        super().__init__(begin, end)
        
        # Przypisujemy pojedyncze miejsce
        self.place = place
        
        # Opcjonalny pracownik
        self.worker = worker

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ShiftPlace):
            return False
        # Porównujemy miejsce (sprawdzamy np. po nazwie lub ID, jeśli to obiekt)
        if self.begin == other.begin and self.end == other.end:
            if getattr(self.place, 'name', self.place) == getattr(other.place, 'name', other.place):
                return True
        return False
    
    def contains(self, shift: Shift) -> bool:
        
        if self.begin <= shift.begin and self.end >= shift.end:
                if isinstance(shift, ShiftPlace):
                     # Sprawdzamy czy to samo miejsce
                    if getattr(self.place, 'name', self.place) == getattr(shift.place, 'name', shift.place):
                        return True 
                else:
                    return True
               
        return False

    #checks houurs and place
    def sameShift(self, shift: ShiftPlace) -> bool:
        if isinstance(shift, ShiftPlace):
            if self.begin == shift.begin and self.end == shift.end:
                if getattr(self.place, 'name', self.place) == getattr(shift.place, 'name', shift.place):
                    return True 
        return False
        
    def serializer(self) -> dict[str, Any]:
        return {
            "__type__": "ShiftPlace",
            # Bezpieczny zapis daty
            "begin": self.begin.isoformat() if hasattr(self.begin, 'isoformat') else str(self.begin),
            "end": self.end.isoformat() if hasattr(self.end, 'isoformat') else str(self.end),
            
            # Pobieramy nazwę lub ID miejsca, aby JSON mógł to zapisać
            "place": self.place.name if hasattr(self.place, 'name') else str(self.place),
            
            # Bezpieczne ID pracownika (jeśli przypisany)
           # "worker": self.worker.id if hasattr(self, 'worker') and hasattr(self.worker, 'id') else None

           #better works with mypy
            "worker": self.worker.id if self.worker is not None else None
        }


