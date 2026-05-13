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
        # Mapa dla szybkiego wyszukiwania pracownika po ID
        self.worker_map = {w.id: w for w in workers}
        # Lista wszystkich dostepnych ID pracownikow (alleli)
        self.worker_ids = [w.id for w in workers]
        
        # To bedzie przechowywac stala kolejnosc slotow dla danego uruchomienia
        self.ordered_slots: List[ShiftPlace] = []

    def prepare_slots(self, month: int, year: int):
        """
        Zbiera wszystkie zmiany ze wszystkich miejsc pracy dla danego miesiaca.
        Musi byc wywolane przed startem algorytmu.
        """
        self.ordered_slots = []
        # Sortujemy miejsca po ID, zeby zawsze miec te sama kolejnosc
        for place in sorted(self.places, key=lambda p: p.id):
            # Zakladamy, ze place.schedule jest juz wypelnione pustymi zmianami 
            # przez scheduler.defaultPlaceSchedule(year, month)
            for shift in sorted(place.schedule, key=lambda s: s.begin):
                self.ordered_slots.append(shift)
        
        return len(self.ordered_slots)

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

    def get_invalid_slots_count(self) -> int:
        """Zwraca liczbe nieobsadzonych zmian (kara dla fitness)"""
        return sum(1 for s in self.ordered_slots if s.worker is None)