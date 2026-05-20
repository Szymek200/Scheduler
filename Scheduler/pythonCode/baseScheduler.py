
from __future__ import annotations
from abc import ABC, abstractmethod


from itertools import product
from datetime import datetime, time, timedelta
from itertools import combinations
from dataclasses import dataclass, field
import copy
from typing import TYPE_CHECKING
from rules import CyclicRule

if TYPE_CHECKING:
    from worker import Worker
    from place import Place
    from shift import ShiftPlace


class BaseScheduler(ABC):
    def __init__(self, workers: list[Worker], places: list [Place]):
        #workers have requested schedule and its requirements
        #places have required shifts to fill  
        
        
        self.placeSchedule = False
        self.ready = 0
        self.places = places
        self.workers = workers

      
    #for every shift we check
    #place and worker rules
    def complyWithRules(self, shift):

        #check only one shift
        #shift inside has every required info
        if shift.place.compliesRules(shift, shift.worker) and shift.worker.compliesRules(shift):
            return True
        return False
    
    @abstractmethod
    def createPlan(self, month, year):
        pass


    #REQUESTED SCHEDULE FOR PLACES

    def defaultPlaceSchedule(self, year, month):

        from shift import ShiftPlace
        start_date = datetime(year, month, 1, 0, 0, 0)
        
        # Obliczamy koniec miesiąca
        if month == 12:
            end_date = datetime(year + 1, 1, 1, 0, 0, 0) - timedelta(seconds=1)
        else:
            end_date = datetime(year, month + 1, 1, 0, 0, 0) - timedelta(seconds=1)
        
        # 2. GENEROWANIE PUSTEGO HARMONOGRAMU DLA MIEJSC
        for place in self.places:
            place.schedule.clear()
            
            for rule in place.rules:
                if isinstance (rule, CyclicRule):
                    pointer_begin = rule.begin.begin
                    pointer_end = rule.begin.end
                    interval = rule.interval
                    
                    # Przewijanie do obecnego miesiąca
                    if pointer_begin < start_date:
                        delta_days = (start_date.date() - pointer_begin.date()).days
                        interval_days = interval.days if hasattr(interval, 'days') else interval
                        
                        # Jeśli interval_days z jakiegoś powodu wynosi 0, zabezpieczamy się przed ZeroDivisionError
                        if interval_days == 0:
                            interval_days = 1
                            
                        jumps = (delta_days // interval_days) + (1 if delta_days % interval_days != 0 else 0)
                        
                        # Tutaj zostaje bez zmian, bo timedelta pozwala na mnożenie przez int
                        pointer_begin += timedelta(days=jumps * interval_days)
                        pointer_end += timedelta(days=jumps * interval_days)
                    while pointer_begin <= end_date:
                        new_shift = ShiftPlace(pointer_begin, pointer_end, place, None)
                        place.schedule.append(new_shift)
                        
                        pointer_begin += interval
                        pointer_end += interval
        
        self.placeSchedule = True

         #REQUESTED SCHEDULE FOR PLACES

        #request schedule which is designed only based on rules for worker
    """
    def defaultRequestedSchedule(self, worker, year, month):

        import rules 
        worker.rqSchedule.clear()

        #defaultPlaceSchedule required first
        if self.placeSchedule == False:
            self.defaultPlaceSchedule( year, month)

        # 3. GENEROWANIE REQUEST SCHEDULE DLA PRACOWNIKA
        for place in self.places:
            for shift in place.schedule:
                # UŻYWAMY FILTRU: sprawdzamy tylko reguły dziedziczące po rules.Rule
                if worker.compliesRules(shift, rules.AvalRule):
                    worker_shift = copy.deepcopy(shift)
                    worker_shift.worker = worker
                    worker.rqSchedule.append(worker_shift)
        """

    def defaultRequestedSchedule(self, worker, year, month):
        import rules 
        from datetime import datetime, timedelta
        import copy

        worker.rqSchedule.clear()

        # 1. Upewniamy się, że grafik miejsc na dany miesiąc istnieje
        if self.placeSchedule == False:
            self.defaultPlaceSchedule(year, month)

        # 2. SANITY CHECK / NAPRAWA TYPÓW DANYCH Z JSON DLA REGUŁ PRACOWNIKA
        # Ponieważ JSON wczytuje daty jako stringi, a interwały jako float, musimy je naprawić
        for rule in worker.rules:
            if isinstance(rule, rules.CyclicRule):
                # Naprawa interwału (jeśli jest float/int sekundy -> zamiana na timedelta)
                if not isinstance(rule.interval, timedelta):
                    rule.interval = timedelta(seconds=float(rule.interval))
                
                # Naprawa obiektu ShiftPlace wewnątrz reguły (jeśli begin/end to stringi)
                if hasattr(rule, 'begin') and rule.begin is not None:
                    if isinstance(rule.begin.begin, str):
                        rule.begin.begin = datetime.fromisoformat(rule.begin.begin)
                    if isinstance(rule.begin.end, str):
                        rule.begin.end = datetime.fromisoformat(rule.begin.end)

        # 3. GENEROWANIE REQUEST SCHEDULE POPRZEZ FILTROWANIE GOTOWEGO GRAFIKU MIEJSC
        for place in self.places:
            for shift in place.schedule:
                
                # Sprawdzamy reguły dostępności (AvalRule)
                if worker.compliesRules(shift, rules.AvalRule):
                    worker_shift = copy.deepcopy(shift)
                    worker_shift.worker = worker
                    worker.rqSchedule.append(worker_shift)

        print(f"DEBUG: Wygenerowano {len(worker.rqSchedule)} zmian dla pracownika {worker.name}")


  #if two schedules have the same shift(without workers)
    def schedulesIntersect(scheduleOne, scheduleTwo):
        scheduleOne.sorted(key=lambda shift: shift.begin)
        scheduleTwo.sorted(key=lambda shift: shift.begin)

        intersected = []
        for i, one in enumerate(scheduleOne):
            for j, two in enumerate(scheduleTwo):

                if two.begin > one.begin:
                    break

                if one.sameShift(two):
                    intersected.append((one, (i, j) ))
            
        return intersected