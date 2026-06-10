
from __future__ import annotations
from abc import ABC, abstractmethod


from itertools import product
from datetime import datetime, time, timedelta
from itertools import combinations
from dataclasses import dataclass, field
import copy
from typing import TYPE_CHECKING

from myExceptions import MonthRange

from rules import Rule, AvalRule, CyclicRule, UnorderedRule

if TYPE_CHECKING:
    from worker import Worker
    from place import Place
    from shift import ShiftPlace


class BaseScheduler(ABC):
    def __init__(self, workers: list[Worker], places: list [Place], month, year):
        #workers have requested schedule and its requirements
        #places have required shifts to fill  

        self.ready = 0
        self.places = places
        self.workers = workers
        self.year = year
        self.month = month

        self.created_month = 0

    def updateDate(self, month: int, year: int):
        self.year = year
        self.month = month
        self.ready = 0 #generated schedule is false

      
    #for every shift we check
    #place and worker rules
    def complyWithRules(self, shift):

        #check only one shift
        #shift inside has every required info
        if shift.place.compliesRules(shift, shift.worker) and shift.worker.compliesRules(shift):
            return True
        return False
    
    @abstractmethod
    def createPlan(self):
        pass


    #REQUESTED SCHEDULE FOR PLACES

    def defaultPlaceSchedule(self, year, month):

        print("Creating place schedule")

        if(month < 0 or month > 11):
            raise MonthRange("Month value out of range")

        from shift import ShiftPlace
        
        # 👇 POPRAWIONO: Konwersja formatu 0-11 na format systemowy 1-12 dla datetime
        system_month = month + 1
        
        start_date = datetime(year, system_month, 1, 0, 0, 0)
        print(f"Begin date: {start_date}")
        
        # Obsługa przejścia z grudnia (12) na styczeń (1) kolejnego roku dla end_date
        if system_month == 12:
            end_date = datetime(year + 1, 1, 1, 0, 0, 0) - timedelta(seconds=1)
        else:
            end_date = datetime(year, system_month + 1, 1, 0, 0, 0) - timedelta(seconds=1)
            
        print(f"End date: {end_date}")
        
        for place in self.places:
            place.schedule.clear()
            print(f"[DEBUG] Miejsce: {place.name} | Reguly: {len(place.rules)}")
            
            for rule in place.rules:
                if isinstance (rule, CyclicRule):
                    interval: timedelta = rule.interval
                    pointer_begin = rule.begin.begin
                    pointer_end = rule.begin.end
                    
                    # Przewijanie do wybranego miesiaca
                    if pointer_begin < start_date:
                        delta_days = (start_date.date() - pointer_begin.date()).days
                        interval_days = interval.days if hasattr(interval, 'days') else int(interval)
                    
                        jumps = (delta_days // interval_days) + (1 if delta_days % interval_days != 0 else 0)
                        
                        pointer_begin += timedelta(days=jumps * interval_days)
                        pointer_end += timedelta(days=jumps * interval_days)
                        
                    while pointer_begin <= end_date:
                        new_shift = ShiftPlace(pointer_begin, pointer_end, place, None)
                        place.schedule.append(new_shift)
                        
                        delta = interval if isinstance(interval, timedelta) else timedelta(days=int(interval))
                        pointer_begin += delta
                        pointer_end += delta


         #REQUESTED SCHEDULE FOR WORKERS


    def defaultRequestedSchedule(self, worker, year = 0, month = 0):
        import rules 
        from datetime import datetime, timedelta
        import copy

        worker.rqSchedule.clear()

        # SANITY CHECK / NAPRAWA TYPÓW DANYCH Z JSON DLA REGUŁ PRACOWNIKA
        for rule in worker.rules:
            if isinstance(rule, rules.CyclicRule):
                if not isinstance(rule.interval, timedelta):
                    rule.interval = timedelta(seconds=float(rule.interval))
                
                if hasattr(rule, 'begin') and rule.begin is not None:
                    if isinstance(rule.begin.begin, str):
                        rule.begin.begin = datetime.fromisoformat(rule.begin.begin)
                    if isinstance(rule.begin.end, str):
                        rule.begin.end = datetime.fromisoformat(rule.begin.end)

        # GENEROWANIE REQUEST SCHEDULE POPRZEZ FILTROWANIE GOTOWEGO GRAFIKU MIEJSC
        for place in self.places:
            for shift in place.schedule:
                if worker.compliesRules(shift, rules.AvalRule):
                    from shift import ShiftPlace
                    worker_shift = ShiftPlace(shift.begin, shift.end, shift.place, worker)
                    worker_shift.worker = worker
                    worker.rqSchedule.append(worker_shift)

        print(f"DEBUG: Wygenerowano {len(worker.rqSchedule)} zmian dla pracownika {worker.name}")


  #if two schedules have the same shift(without workers)
    def schedulesIntersect(self, scheduleOne, scheduleTwo):
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