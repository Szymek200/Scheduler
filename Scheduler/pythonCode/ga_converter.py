# -*- coding: utf-8 -*-
import numpy as np
from typing import List, Dict
from shift import ShiftPlace
from worker import Worker
from place import Place

class GAConverter:
    def __init__(self, workers: List[Worker], places: List[Place]):
        self.workers = workers
        self.places = places
        #slownik: id and worker
        self.worker_map = {w.id: w for w in workers}
        # Lista wszystkich dostepnych ID pracownikow (alleli)
        
        # To bedzie przechowywac stala kolejnosc slotow dla danego uruchomienia
        self.ordered_slots: List[ShiftPlace] = []

    def prepare_slots(self, month: int, year: int, availability_cache: dict) -> list:
        """
        Zbiera wszystkie zmiany i buduje ograniczoną przestrzeń genów (gene_space)
        na podstawie cache'u dostępności pracowników.
        """
        self.ordered_slots = []
        gene_space = [] 
        
       
        for place in sorted(self.places, key=lambda p: p.id):
            
            for shift in sorted(place.schedule, key=lambda s: s.begin):
                self.ordered_slots.append(shift)

             
                #changing shift to text from object
                shift_key = f"{shift.begin.isoformat()}_{shift.end.isoformat()}_{getattr(shift.place, 'name', shift.place)}"

                
                allowed_workers_for_this_shift = []
                for w in self.workers:
                    
                    worker_cache = availability_cache.get(w.id, set()) #we take out set of all shifts of a working
                    if shift_key in worker_cache:
                        allowed_workers_for_this_shift.append(w.id)

                #if no worker wants to work this day we put everyone - so alg. can create any answear
                if not allowed_workers_for_this_shift:
                    allowed_workers_for_this_shift = list(self.worker_map.keys())

                #for every shift in ordered_slots is coresponding list of workers who can work that shift
                gene_space.append(allowed_workers_for_this_shift)
        
        return gene_space

    def to_vector(self) -> np.ndarray:
        """
        Konwertuje aktualne przypisania w obiektach ShiftPlace na wektor ID (dla GA).
        """
        vector = []
        for shift in self.ordered_slots:
            if shift.worker:
                vector.append(shift.worker.id)
            else:
                vector.append(-1) # -1 oznacza nieobsadzona zmiane
        return np.array(vector)

    def update_objects_from_vector(self, vector: np.ndarray):
        """
        Bierze rozwiazanie z GA (tablice ID) i aktualizuje obiekty ShiftPlace oraz Worker.
        """
        # Najpierw czyscimy stare przypisania u pracownikow
        for w in self.workers:
            w.schedule = []

        for i, worker_id in enumerate(vector):
            shift = self.ordered_slots[i]
            # worker_id moze byc floatem w PyGAD, rzutujemy na int
            w_id = int(worker_id)
            
            if w_id in self.worker_map:
                worker = self.worker_map[w_id]
                shift.worker = worker
                worker.addAcqShift(shift) # Dodaje do worker.schedule
            else:
                shift.worker = None

    def update_all_objects_from_vector(self, vector: np.ndarray):
        for w in self.workers:
            w.schedule = []

        for p in self.places:
            p.schedule = []

        for i, worker_id in enumerate(vector):
            shift = self.ordered_slots[i]
           
            w_id = int(worker_id)
            
            if w_id in self.worker_map:
                worker = self.worker_map[w_id]
                shift.worker = worker
                worker.addAcqShift(shift) # Dodaje do worker.schedule

                if shift.place in self.places:
                    shift.place.addShift(shift)
                else:
                    shift.place = None

            else:
                shift.worker = None

        


    def get_invalid_slots_count(self) -> int:
        """Zwraca liczbe nieobsadzonych zmian (kara dla fitness)"""
        return sum(1 for s in self.ordered_slots if s.worker is None)