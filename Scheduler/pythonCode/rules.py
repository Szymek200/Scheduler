# -*- coding: utf-8 -*-
from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from copy import deepcopy
from typing import Any, TYPE_CHECKING
from shift import ShiftPlace

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

    def __init__(self, begin: ShiftPlace, interval: timedelta, name: str):
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
            "interval": self.interval.total_seconds()
        }
    
    def uncompliedShifts(self, shift: ShiftPlace) -> list[ShiftPlace]:
        from shift import ShiftPlace
        if not self.isFulfilled(shift):
            return [shift]
        return []

class RightRule(Rule):
    def __init__(self, owner, name: str):
        super().__init__(name)
        #worker or place which has this rule
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
        # 1. Pobieramy przepracowany czas
        hoursWorked = worker.howManyHours()
        
        # 2. Sprawdzamy czy mieści się w normie (wartość +/- odchylenie)
        # Jeśli tak, zwracamy 0 (brak kary)
        if (self.value - self.deviation) <= hoursWorked <= (self.value + self.deviation):
            return 0.0
        
        # 3. Jeśli nie, liczymy różnicę w godzinach
        # Używamy abs(), żeby kara była zawsze dodatnia niezależnie czy ma za mało czy za dużo godzin
        diff_seconds = abs(self.value.total_seconds() - hoursWorked.total_seconds())
        diff_hours = diff_seconds / 3600
        
        # Zwracamy karę pomnożoną przez wagę (HARD_PENALTY)
        return float(diff_hours * HARD_PENALTY)


    def serializer(self):
        return {
            "__type__": "Etat Rule",
            "id": self.id,
            "owner": self.owner.id if getattr(self, 'owner', None) is not None else None, #when this rule is used for place
            "name": self.name,
            "value": self.value.total_seconds(),
            "deviation": self.deviation.total_seconds()

        }

class FreeWeekend(RightRule):
    def __init__(self, owner, name, quantity = 2):
        super().__init__(owner, name)
      
        self.name = name
        self.quantity = quantity

        self._cached_weekend_days: set[int] = None
        self._cached_period: tuple[int, int] = (0, 0) # year, month

    #it calculates when there are weekend days in the month
    def _get_weekend_days(self, month: int, year: int):
        if self._cached_weekend_days is not None and self._cached_period == (year, month):
            return self._cached_weekend_days

        weekend_days = set()
        pointer = datetime(year, month, 1)
        
        while pointer.month == month:
            # 5 = Sobota, 6 = Niedziela (w Pythonie .weekday())
            if pointer.weekday() in (5, 6):
                weekend_days.add(pointer.day)
            pointer += timedelta(days=1)
        
        self._cached_weekend_days = weekend_days
        self._cached_period = (year, month)
    

    def isFulfilled(self, shift):

        checkedMonth = shift.begin.month
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
        # 1. ZABEZPIECZENIE: Jeśli pracownik nie ma zmian, nie ma kary.
        if not worker.schedule:
            return 0.0

        # 2. POBIERANIE DATY: Musimy wiedzieć, który to miesiąc i rok.
        first_shift = worker.schedule[0]
        m = first_shift.begin.month
        y = first_shift.begin.year

        # 3. CACHE: Inicjalizujemy dni weekendowe tylko jeśli się zmienił miesiąc/rok.
        if self._cached_weekend_days is None or self._cached_period != (y, m):
            self._get_weekend_days(m, y)

        weekend_working_hours = 0.0
        worked_weekend_days = set()

        # 4. LICZENIE PRZEPRACOWANYCH GODZIN W WEEKENDY
        for shift in worker.schedule:
            # Sprawdzamy czy początek lub koniec zmiany wypada w weekend
            is_start_weekend = shift.begin.day in self._cached_weekend_days
            is_end_weekend = shift.end.day in self._cached_weekend_days
            
            if is_start_weekend or is_end_weekend:
                if is_start_weekend:
                    worked_weekend_days.add(shift.begin.day)
                if is_end_weekend:
                    worked_weekend_days.add(shift.end.day)
               
                weekend_working_hours += shift.duration().total_seconds() / 3600

        # 5. LICZENIE WOLNYCH WEEKENDÓW (Twoja logika z poprawionym total_weekends)
        sorted_days = sorted(list(self._cached_weekend_days))
        actual_total_weekends = 0
        occupied_weekends = 0
        
        i = 0
        while i < len(sorted_days):
            current_day = sorted_days[i]
            # Sprawdzamy czy to para (Sobota+Niedziela)
            if i + 1 < len(sorted_days) and sorted_days[i+1] == current_day + 1:
                actual_total_weekends += 1
                if current_day in worked_weekend_days or sorted_days[i+1] in worked_weekend_days:
                    occupied_weekends += 1
                i += 2 # Skok o parę
            else:
                # Samotny dzień weekendowy na początku/końcu miesiąca
                actual_total_weekends += 1
                if current_day in worked_weekend_days:
                    occupied_weekends += 1
                i += 1

        free_weekends_count = actual_total_weekends - occupied_weekends

        # 6. WYNIK: Jeśli wolnych weekendów jest za mało, dajemy karę.
        if free_weekends_count >= self.quantity:
            return 0.0
        else:
            # Kara to liczba przepracowanych godzin w weekendy * waga
            return float(weekend_working_hours * HARD_PENALTY * 10)


    
    def serializer(self):
        return{
            "__type__": "FreeWeekend",
            "id": self.id,
            "owner": self.owner.id if getattr(self, 'owner', None) is not None else None,
            "name": self.name,
            "quantity": self.quantity

        }
        



class BetweenShifts(RightRule):
    def __init__(self, owner, name, value):
       
        super().__init__(owner, name)
        self.value = value
    

    #to do 
    def isFulfilled(self, shift: ShiftPlace):

        if not self.owner or not hasattr(self.owner, 'schedule'):
            return True

        # 2. Tworzymy tymczasową listę: dotychczasowy grafik pracownika + nowo sprawdzana zmiana
        # Dzięki temu sprawdzamy, czy ta nowa zmiana nie koliduje z obecnym grafikiem
        combined_schedule = self.owner.schedule + [shift]

        # 3. Sortujemy po czasie rozpoczęcia zmian
        sorted_schedule = sorted(combined_schedule, key=lambda x: x.begin)

        # 4. Sprawdzamy odstępy między wszystkimi kolejnymi zmianami
        for i in range(1, len(sorted_schedule)):
            if sorted_schedule[i].begin - sorted_schedule[i-1].end < self.value:
                return False

        return True


    def completion(self, worker):
        if len(worker.schedule) < 2:
            return 0.0
        
        penalty = 0.0
        # Sortujemy grafik chronologicznie
        sorted_sched = sorted(worker.schedule, key=lambda x: x.begin)
        
        for i in range(1, len(sorted_sched)):
            # Odpoczynek to czas od końca poprzedniej do początku obecnej zmiany
            actual_rest = sorted_sched[i].begin - sorted_sched[i-1].end
            
            if actual_rest < self.value:
                # KARA: ile godzin brakuje do wymaganego odpoczynku
                missing_seconds = (self.value - actual_rest).total_seconds()
                missing_hours = missing_seconds / 3600
                penalty += missing_hours * HARD_PENALTY
                
        return float(penalty)
                
    def serializer(self):
        return {
            "__type__": "BetweenShifts",
            "id": self.id,
            "owner": getattr(self.owner, 'id', self.owner) if self.owner is not None else None,
            "name": self.name,
            "value": self.value.total_seconds() if hasattr(self.value, 'total_seconds') else self.value
        }


# Dodaj na samym końcu pliku rules.py

def deserialize_rule(rule_data, entity):
    from worker import Worker
    from shift import ShiftPlace
    
    rule_type = rule_data.get("__type__")
    rule_name = rule_data.get("name", "Unnamed")
    rule_id = rule_data.get("id")
    
    # DEBUG: Zobaczymy co program widzi w pliku
    print(f"[LOADER] Trying to load rule: {rule_name} of type: {rule_type}")

    new_rule = None

    # Dopasowanie typów - upewnij się, że te stringi są identyczne jak w pliku JSON!
    if rule_type == "FreeWeekend":
        quantity = rule_data.get("quantity", 2)
        new_rule = FreeWeekend(entity, rule_name, quantity)

    elif rule_type == "BetweenShifts":
        val = rule_data.get("value", 39600)
        new_rule = BetweenShifts(entity, rule_name, timedelta(seconds=float(val)))

    elif rule_type == "CyclicRule":
        begin_data = rule_data.get("begin", {})
        interval_val = rule_data.get("interval", 1)
        try:
            b_dt = datetime.fromisoformat(begin_data["begin"])
            e_dt = datetime.fromisoformat(begin_data["end"])
            p_name = begin_data.get("place", "")
            # Tworzymy obiekt pomocniczy dla reguły
            start_shift = ShiftPlace(b_dt, e_dt, p_name, entity if isinstance(entity, Worker) else None)
            
            # Decyzja: czy interwał to dni czy sekundy?
            if float(interval_val) > 1000: # sekundy
                delta = timedelta(seconds=float(interval_val))
            else: # dni
                delta = timedelta(days=int(interval_val))
                
            new_rule = CyclicRule(start_shift, delta, rule_name)
        except Exception as e:
            print(f"[LOADER ERROR] CyclicRule fail: {e}")

    elif rule_type in ["Etat Rule", "EtatRule"]:
        try:
            v = rule_data.get("value", 0)
            d = rule_data.get("deviation", 0)
            new_rule = EtatRule(entity, rule_name, timedelta(seconds=float(v)), timedelta(seconds=float(d)))
        except Exception as e:
            print(f"[LOADER ERROR] EtatRule fail: {e}")

    if new_rule:
        if rule_id is not None:
            new_rule.id = rule_id
        print(f"[LOADER] SUCCESS: Added {rule_name} to {entity.name}")
        return new_rule
    else:
        print(f"[LOADER WARNING] FAILED to recognize rule type: {rule_type}")
        return None