
from abc import ABC, abstractmethod

from worker import Worker
from place import Place
from shift import ShiftPlace
from itertools import product
from datetime import datetime, time, timedelta
from itertools import combinations
from dataclasses import dataclass, field
import copy
import utils

from rules import *


class BaseScheduler(ABC):
    def __init__(self, workers, places):
        #workers have requested schedule and its requirements
        #places have required shifts to fill
        
        if not (isinstance(workers, list) and all(isinstance(item, Worker) for item in workers)):
            return -1

        if not (isinstance(places, list) and all(isinstance(item, Place) for item in places)):
            return -1
        
        
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
                if rule.type_name == "cyclic":
                    pointer_begin = rule.begin.begin
                    pointer_end = rule.begin.end
                    interval = rule.interval
                    
                    # Przewijanie do obecnego miesiąca
                    if pointer_begin < start_date:
                        delta_days = (start_date.date() - pointer_begin.date()).days
                        jumps = (delta_days // interval) + (1 if delta_days % interval != 0 else 0)
                        pointer_begin += timedelta(days=jumps * interval)
                        pointer_end += timedelta(days=jumps * interval)

                    while pointer_begin <= end_date:
                        new_shift = ShiftPlace(pointer_begin, pointer_end, place, None)
                        place.schedule.append(new_shift)
                        
                        pointer_begin += timedelta(days=interval)
                        pointer_end += timedelta(days=interval)
        
        self.placeSchedule = True

         #REQUESTED SCHEDULE FOR PLACES

        #request schedule which is designed only based on rules for worker
    def defaultRequestedSchedule(self, worker, year, month):
        worker.rqSchedule.clear()

        #defaultPlaceSchedule required first
        if self.placeSchedule == False:
            self.defaultPlaceSchedule( year, month)

        # 3. GENEROWANIE REQUEST SCHEDULE DLA PRACOWNIKA
        for place in self.places:
            for shift in place.schedule:
                # UŻYWAMY FILTRU: sprawdzamy tylko reguły dziedziczące po rules.Rule
                if worker.compliesRulesRequest(shift, Rule):
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