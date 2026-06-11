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
        self.worker_ids = [w.id for w in workers]
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


    
    def repair_solution(self, vector: np.ndarray, gene_space: list) -> np.ndarray:
        """
        Przechodzi przez wektor i jeśli wykryje nakładanie zmian u pracownika,
        próbuje przypisać tę zmianę komuś innemu z gene_space.
        """
        self.update_objects_from_vector(vector)
        repaired_vector = vector.copy()
        
        for worker in self.workers:
            sorted_sched = sorted(worker.schedule, key=lambda x: x.begin)
            for i in range(1, len(sorted_sched)):
                # Wykryto overlap lub brak wymaganego odpoczynku
                if sorted_sched[i].begin < sorted_sched[i-1].end or (sorted_sched[i].begin - sorted_sched[i-1].end < worker.getBetweenShiftTime()):
                    conflict_shift = sorted_sched[i]
                    # Znajdź indeks tego slotu w ordered_slots
                    slot_idx = self.ordered_slots.index(conflict_shift)
                    
                    # Pobierz listę alternatywnych pracowników dla tego slotu z gene_space
                    allowed_workers = gene_space[slot_idx]
                    
                    # Znajdź pierwszego pracownika z listy, który NIE ma wtedy konfliktu
                    backup_worker_id = None
                    for alt_id in allowed_workers:
                        if alt_id != worker.id:
                            alt_worker = self.worker_map[alt_id]
                            # Szybkie sprawdzenie czy alt_worker nie ma wtedy zmiany
                            has_conflict = any(s.begin < conflict_shift.end and conflict_shift.begin < s.end for s in alt_worker.schedule)
                            if not has_conflict:
                                backup_worker_id = alt_id
                                break
                    
                    if backup_worker_id is not None:
                        repaired_vector[slot_idx] = backup_worker_id
                        # Aktualizujemy obiekt w locie, żeby kolejne iteracje pętli widziały zmianę
                        conflict_shift.worker = self.worker_map[backup_worker_id]
                        
        return repaired_vector

    def update_all_objects_from_vector(self, vector: np.ndarray):
        for w in self.workers:
            w.schedule = []

        for p in self.places:
            p.schedule = []

        place_map = {p.name: p for p in self.places}

        for i, worker_id in enumerate(vector):
            shift = self.ordered_slots[i]
            w_id = int(worker_id)
            
            if w_id in self.worker_map:
                worker = self.worker_map[w_id]
                shift.worker = worker
                worker.addAcqShift(shift) 

                # Sprawdź czy shift.place to string czy obiekt
                p_name = shift.place.name if hasattr(shift.place, 'name') else shift.place
                
                if p_name in place_map:
                    actual_place = place_map[p_name]
                    shift.place = actual_place  # Podmieniamy string na właściwy obiekt Place
                    actual_place.schedule.append(shift) # Dodajemy zmianę do grafiku miejsca
            else:
                shift.worker = None


    def get_invalid_slots_count(self) -> int:
        """Zwraca liczbe nieobsadzonych zmian (kara dla fitness)"""
        return sum(1 for s in self.ordered_slots if s.worker is None)