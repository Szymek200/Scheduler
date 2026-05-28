from __future__ import annotations
from datetime import datetime, timedelta
from abc import abstractmethod
from typing import TYPE_CHECKING
from constans import HARD_PENALTY

from .Rule import Rule

if TYPE_CHECKING:
    from shift import ShiftPlace
    from worker import Worker

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
        if self.owner is not None:
            owner_id = self.owner.id if hasattr(self.owner, 'id') else int(self.owner)
        else:
            owner_id = None

        return {
            "__type__": "Etat Rule",
            "id": self.id,
            "owner": owner_id,
            "name": self.name,
            "value": self.value.total_seconds() if hasattr(self.value, 'total_seconds') else self.value,
            "deviation": self.deviation.total_seconds() if hasattr(self.deviation, 'total_seconds') else self.deviation
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

        if not isinstance(checkedMonth, int) or not (1 <= checkedMonth <= 12):
            raise ValueError("Parametr 'checkedMonth' musi być liczbą całkowitą z zakresu 1-12")

        pointer = datetime.today() 
        pointer = pointer.replace(month=checkedMonth, day=1)

        # Przewijamy do pierwszej soboty w miesiącu
        while pointer.strftime("%A") != "Saturday":
            pointer += timedelta(days=1)

        # Sprawdzamy wszystkie weekendy w danym miesiącu
        while pointer.month == checkedMonth:
            # POPRAWIONO: Inkrementacja daty musi być wykonywana ZAWSZE na końcu pętli
            if pointer.strftime("%A") not in ("Saturday", "Sunday"):
                emptyWeekend += 1
            pointer += timedelta(days=1)

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
        # Bezpieczne wyciąganie ID właściciela (niezależnie czy self.owner to obiekt, czy już surowy int)
        if self.owner is not None:
            owner_id = self.owner.id if hasattr(self.owner, 'id') else int(self.owner)
        else:
            owner_id = None

        return {
            "__type__": "FreeWeekend",
            "id": self.id,
            "owner": owner_id,
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
        if self.owner is not None:
            owner_id = self.owner.id if hasattr(self.owner, 'id') else int(self.owner)
        else:
            owner_id = None

        return {
            "__type__": "BetweenShifts",
            "id": self.id,
            "owner": owner_id,
            "name": self.name,
            "value": self.value.total_seconds() if hasattr(self.value, 'total_seconds') else self.value
        }