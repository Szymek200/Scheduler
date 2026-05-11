from calendar import month

import pygad
import numpy
from pythonCode import worker
from pythonCode.baseScheduler import BaseScheduler
from rules import RightRule, AvalRule

HARD_PENALTY = 1000
SOFT_PENALTY = 1

class ScheduleValidator(BaseScheduler):

    def __init__(self, workers, places, month, year):
        self.workers = workers
        self.places = places
        self.month = month
        self.year = year


    #errros checked by not hours outside requested schedule
    def check_aval_rules(self):

        #generating requested schedule for every worker based on his rules
        for worker in self.workers:
             self.defaultRequestedSchedule(self, worker, self.year, self.month)

        #checking if there is any shift is schedule outside of requested schedule=

        violations = {}

        for worker in self.workers:

            for assigned_shift in worker.schedule:

                conflict_count_hours = 0
                # Sprawdzamy, czy przypisana zmiana istnieje w rqSchedule
                # Używamy any() i metody sameShift() dla pewności porównania danych, a nie instancji
                is_available = any(assigned_shift.sameShift(rq_shift) for rq_shift in worker.rqSchedule)
            
                if not is_available:
                    conflict_count_hours += assigned_shift.duration_hours()  
        
            # Zapisujemy wynik dla konkretnego ID pracownika
            violations[worker.id] = conflict_count_hours

        return violations * SOFT_PENALTY;

        
  
    def fitness_func(self, shedule_short):

        #schedule_short - dictionary, place id, shifts

        #adding schedule to place objects

        for place in self.places:
            place.schedule = shedule_short.get(place.id, [])
        
        worker_map = {w.id: w for w in self.workers}

        for worker in self.workers:
            worker.schedule.clear()

        #adding shifts to workers

        for place in self.places:
            for shift in place.shifts:
                if shift.worker:
                    worker_map.get(shift.worker.id).schedule.append(shift)

   

        penalty= self.check_aval_rules()
  
    #to do. - place roles go to workers or place rules are useless unless po rqschedule
        for worker in self.workers:
            
            w_rules = [rule for rule in worker.rules if isinstance(rule, RightRule)]

            for rule in w_rules:
                        if isinstance(rule, RightRule):
                            penalty += rule.completion(worker)

        # 4. Calculate Final Fitness Score
        # We want to maximize this value. 
        # Hard rules are weighted heavily so any solution breaking a hard rule 
        # is significantly worse than one only breaking soft rules.
        # Adding 0.000001 prevents division by zero.


        fitness = 1.0 / penalty
        return fitness