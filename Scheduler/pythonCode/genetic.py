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

from constans import HARD_PENALTY, SOFT_PENALTY

from ga_converter import GAConverter
import pygad



class GeneticScheduler(BaseScheduler):

    def __init__(self, workers: list[Worker], places: list[Place], month, year):

        super().__init__(workers, places, month, year)

        self.converter = GAConverter(workers, places);

        print(f"[GA] Przygotowuje dane dla {len(self.workers)} pracownikow...")

        # Szybki słownik dostepnosci
        #klucz - worker id
        #wartosc - wszystkie zmiany w formacie tekstowym
        self.availability_cache = {} 
        
          
      
    def hard_rules(self) -> float:
        penalty: float = 0.0
        
        for worker in self.workers:
            # --- 1. OVERLAP CHECK (Kluczowe!) ---
            # Sortujemy grafik pracownika, żeby sprawdzić czy zmiany na siebie nie nachodzą
            sorted_sched = sorted(worker.schedule, key=lambda x: x.begin)
            for i in range(1, len(sorted_sched)):
                if sorted_sched[i].begin < sorted_sched[i-1].end:
                    # Jeśli zmiany się pokrywają, dajemy GIGANTYCZNĄ karę
                    # To sprawi, że "klonowanie" będzie najgorszą rzeczą dla GA
                    penalty += 100000.0 

            # --- 2. EXISTING RULES (BetweenShifts, Etat, etc.) ---
            for rule in worker.rules:
                if isinstance(rule, RightRule):
                    penalty += rule.completion(worker)
        
        return float(penalty)
    
    def fitness_func(self, ga_instance, solution, solution_idx):
        self.converter.update_objects_from_vector(solution)
        
        penalty = 0.0
        # 1. Kara za puste sloty (zostawiamy wysoko)
        penalty += self.converter.get_invalid_slots_count() * 5000.0
        
        # 2. Twoje reguły (w tym Overlap Check z hard_rules)
        penalty += self.hard_rules()
        
        # 3. --- NAGRODA ZA PREFERENCJE (Zwiększona) ---
        bonus = 0.0
        for worker in self.workers:
            w_cache = self.availability_cache.get(worker.id, set())
            for shift in worker.schedule:
                # Upewnij się, że ten klucz jest taki sam jak w createPlan!
                key = f"{shift.begin.isoformat()}_{shift.end.isoformat()}_{getattr(shift.place, 'name', shift.place)}"
                if key in w_cache:
                    bonus += 500.0 # Zwiększamy nagrodę dziesięciokrotnie
        
        # Odejmujemy bonus od kary
        penalty -= bonus
        
        # Zabezpieczenie: fitness nie może być liczony z ujemnej kary
        if penalty < 0: 
            penalty = 0.0
        
        return 1.0 / (float(penalty) + 0.001)
    
    def createPlan(self):

        self.defaultPlaceSchedule(self.year, self.month)
        
        self.availability_cache.clear()
        
        for worker in self.workers:
            # Generujemy grafik życzeń na właściwy, wybrany w danej chwili miesiąc
            self.defaultRequestedSchedule(worker, self.year, self.month) 
            
            # Budujemy aktualny zestaw kluczy dla tego pracownika
            self.availability_cache[worker.id] = {
                f"{s.begin.isoformat()}_{s.end.isoformat()}_{getattr(s.place, 'name', s.place)}" 
                for s in worker.rqSchedule
            }


        # --- TRYB TESTOWY: Male wartosci, zeby sprawdzic czy dziala ---

        custom_gene_space = self.converter.prepare_slots(self.month, self.year, self.availability_cache)

        num_genes:int = len(self.converter.ordered_slots)

        #ga_instance = pygad.GA(
        #    num_generations=200,           # Tylko 20 pokolen na start
        #    num_parents_mating=5,
        #    fitness_func=self.fitness_func,
        #    sol_per_pop=20,               # Tylko 20 osobnikow
        #    num_genes=num_genes,
        #    gene_space=custom_gene_space,
        #    on_generation=self.on_generation, # Widzisz postep w konsoli!
        #    mutation_percent_genes=5
        #)

        self.created_month = self.month

        ga_instance = pygad.GA(
            num_generations=200,
            sol_per_pop=100,
            num_parents_mating=30,
            fitness_func=self.fitness_func,
            num_genes=num_genes,
            gene_space=self.converter.worker_ids, 
            on_generation=self.on_generation,
            mutation_percent_genes=15,    # Wyższa mutacja, żeby "wybić" algorytm z zastoju
            mutation_type="random",       # Szukamy losowo nowych rozwiązań
            keep_elitism=5                # Trzymamy 5 najlepszych grafików
        )

        #for ui what month schedule did we created
        self.created_month = self.month
        
        print(f"[GA] Start ewolucji (Slotow: {num_genes})...")
        ga_instance.run()
        
        solution, fitness, idx = ga_instance.best_solution()
        self.converter.update_objects_from_vector(solution)
        print(f"[GA] Zakonczono. Wynik: {fitness:.6f}")

        self.ready = 1
        return 1
        #return solution
    
    def on_generation(self,ga_instance):

        from PySide6.QtWidgets import QApplication
        QApplication.processEvents()

        print("Generation : ", ga_instance.generations_completed)
        print("Fitness of the best solution :", ga_instance.best_solution()[1])