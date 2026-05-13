# -*- coding: utf-8 -*-
from __future__ import annotations
import pygad
import numpy as np
from datetime import datetime, timedelta

from baseScheduler import BaseScheduler
from rules import RightRule, AvalRule
from worker import Worker
from place import Place
from shift import ShiftPlace
from ga_converter import GAConverter

class GeneticScheduler(BaseScheduler):
    def __init__(self, workers: list[Worker], places: list[Place], month: int, year: int):
        super().__init__(workers, places)
        self.month = month
        self.year = year
        self.converter = GAConverter(workers, places)
        self.num_genes = self.converter.prepare_slots(month, year)
        
        # --- OPTYMALIZACJA 1: Generujemy zyczenia RAZ ---
        print(f"[GA] Przygotowuje dane dla {len(self.workers)} pracownikow...")
        self.availability_cache = {} # Szybki słownik dostepnosci
        
        for worker in self.workers:
            self.defaultRequestedSchedule(worker, self.year, self.month)
            # Tworzymy zestaw unikalnych kluczy (data+godzina+miejsce) dla błyskawicznego sprawdzania
            self.availability_cache[worker.id] = {
                f"{s.begin.isoformat()}_{getattr(s.place, 'name', s.place)}" 
                for s in worker.rqSchedule
            }

    def fast_check_aval(self) -> int:
        """Blyskawiczne sprawdzanie dostepnosci przy uzyciu cache"""
        penalty = 0
        for worker in self.workers:
            w_cache = self.availability_cache.get(worker.id, set())
            for shift in worker.schedule:
                # Tworzymy klucz dla obecnej zmiany
                key = f"{shift.begin.isoformat()}_{getattr(shift.place, 'name', shift.place)}"
                if key not in w_cache:
                    # Kara 10 za kazda godzine poza dostepnoscia
                    penalty += int(shift.duration().total_seconds() // 3600) * 10
        return penalty

    def fitness_func(self, ga_instance, solution, solution_idx):
        # 1. Update obiektow (to musi byc, ale robimy to raz na osobnika)
        self.converter.update_objects_from_vector(solution)
        
        penalty = 0
        # 2. Kara za puste sloty (bardzo wysoka)
        penalty += self.converter.get_invalid_slots_count() * 1000
        
        # 3. Szybka kara za dostepnosc
        penalty += self.fast_check_aval()
        
        # 4. Reguly RightRules (Etat, przerwy)
        for worker in self.workers:
            for rule in worker.rules:
                if isinstance(rule, RightRule):
                    penalty += rule.completion(worker)

        return 1.0 / (penalty + 0.001)

    def on_generation(self, ga_instance):
        """Wyswietla postep w kazdej generacji"""
        best_sol, best_fit, _ = ga_instance.best_solution()
        print(f"-> Pokolenie {ga_instance.generations_completed} | Fitness: {best_fit:.6f}")

    def createPlan(self, month: int, year: int):
        # --- TRYB TESTOWY: Male wartosci, zeby sprawdzic czy dziala ---
        ga_instance = pygad.GA(
            num_generations=20,           # Tylko 20 pokolen na start
            num_parents_mating=5,
            fitness_func=self.fitness_func,
            sol_per_pop=20,               # Tylko 20 osobnikow
            num_genes=self.num_genes,
            gene_space=self.converter.worker_ids,
            on_generation=self.on_generation, # Widzisz postep w konsoli!
            mutation_percent_genes=5
        )
        
        print(f"[GA] Start ewolucji (Slotow: {self.num_genes})...")
        ga_instance.run()
        
        solution, fitness, idx = ga_instance.best_solution()
        self.converter.update_objects_from_vector(solution)
        print(f"[GA] Zakonczono. Wynik: {fitness:.6f}")
        return solution