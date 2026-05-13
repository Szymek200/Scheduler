
from __future__ import annotations
from abc import ABC, abstractmethod


from itertools import product
from datetime import datetime, time, timedelta
from itertools import combinations
from dataclasses import dataclass, field
import copy
from typing import TYPE_CHECKING

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
        print(f"\n[DEBUG] Rozpoczynam generowanie dla {month}/{year}")
        
        start_date = datetime(year, month, 1, 0, 0, 0)
        
        # Obliczamy koniec miesiąca
        if month == 12:
            end_date = datetime(year + 1, 1, 1, 0, 0, 0) - timedelta(seconds=1)
        else:
            end_date = datetime(year, month + 1, 1, 0, 0, 0) - timedelta(seconds=1)
        
        for place in self.places:
            place.schedule.clear()
            print(f"[DEBUG] Miejsce: {place.name} | Reguly: {len(place.rules)}")
            
            for rule in place.rules:
                # Sprawdzenie czy to regula cykliczna
                is_cyclic = getattr(rule, 'type_name', '').lower() == "cyclic" or rule.__class__.__name__ == "CyclicRule"
                
                if is_cyclic:
                    print(f"[DEBUG] -> Regula: {rule.name}")
                    pointer_begin = rule.begin.begin
                    pointer_end = rule.begin.end
                    
                    # Obsluga interwalu (zamiana na int jesli trzeba)
                    raw_interval = rule.interval
                    int_interval = raw_interval.days if hasattr(raw_interval, 'days') else int(raw_interval)
                    
                    # Przewijanie do wybranego miesiaca
                    if pointer_begin < start_date:
                        delta_days = (start_date.date() - pointer_begin.date()).days
                        jumps = (delta_days // int_interval) + (1 if delta_days % int_interval != 0 else 0)
                        pointer_begin += timedelta(days=jumps * int_interval)
                        pointer_end += timedelta(days=jumps * int_interval)

                    count = 0
                    while pointer_begin <= end_date:
                        new_shift = ShiftPlace(pointer_begin, pointer_end, place, None)
                        place.schedule.append(new_shift)
                        
                        pointer_begin += timedelta(days=int_interval)
                        pointer_end += timedelta(days=int_interval)
                        count += 1
                    
                    print(f"[DEBUG]    Dodano {count} slotow")
        
        self.placeSchedule = True

         #REQUESTED SCHEDULE FOR PLACES

        #request schedule which is designed only based on rules for worker
    def defaultRequestedSchedule(self, worker, year, month):
        from shift import ShiftPlace
        import rules 
        worker.rqSchedule.clear()

        #defaultPlaceSchedule required first
        if self.placeSchedule == False:
            self.defaultPlaceSchedule( year, month)

        # 3. GENEROWANIE REQUEST SCHEDULE DLA PRACOWNIKA
        for place in self.places:
            for shift in place.schedule:
                # UŻYWAMY FILTRU: sprawdzamy tylko reguły dziedziczące po rules.Rule
                if worker.compliesRules(shift, rules.Rule):
                    worker_shift = copy.deepcopy(shift)
                    worker_shift.worker = worker
                    worker.rqSchedule.append(worker_shift)


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