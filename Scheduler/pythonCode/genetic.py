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

class GeneticScheduler(BaseScheduler):

    def __init__(self, workers: list[Worker], places: list[Place], month, year):
        super().__init__(workers, places, month, year)
        self.converter = GAConverter(workers, places)
        print(f"[GA] Przygotowuje dane dla {len(self.workers)} pracownikow...")
        self.availability_cache = {} 
        
    def hard_rules(self) -> float:
        penalty: float = 0.0
        
        for worker in self.workers:
            # DETEKCJA OVERLAPU I BRAKU ODPOCZYNKU ---
            sorted_sched = sorted(worker.schedule, key=lambda x: x.begin)
            for i in range(1, len(sorted_sched)):
                # Zmiany nachodzą na siebie
                if sorted_sched[i].begin < sorted_sched[i-1].end:
                    penalty += 500000.0  # Ekstremalna kara za jednoczesną pracę
                
                # Zmiany są bezpośrednio po sobie (brak wymaganych 11h odpoczynku)
                elif sorted_sched[i].begin - sorted_sched[i-1].end < timedelta(hours=11):
                    penalty += 150000.0  # Bardzo wysoka kara za brak przerwy między zmianami

            # pozostale reguly
            for rule in worker.rules:
                if isinstance(rule, RightRule):
                    penalty += rule.completion(worker)
        
        return float(penalty)
    
    def fitness_func(self, ga_instance, solution, solution_idx):


        custom_gene_space = ga_instance.gene_space # Pobieramy przestrzeń genów
        repaired_solution = self.converter.repair_solution(solution, custom_gene_space)
        
        # Nadpisujemy rozwiązanie w PyGAD, żeby algorytm zapamiętał naprawionego osobnika
        ga_instance.population[solution_idx] = repaired_solution
        self.converter.update_objects_from_vector(solution)
        
        invalid_slots_penalty = self.converter.get_invalid_slots_count() * 10000.0
        rules_penalty = self.hard_rules()
        
        
        if rules_penalty >= 150000.0:
            return 1.0 / (rules_penalty * 100.0) # Bardzo, bardzo blisko 0
            
        total_penalty = invalid_slots_penalty + rules_penalty
        
        bonus = 0.0
        if rules_penalty < 10000.0: 
            for worker in self.workers:
                w_cache = self.availability_cache.get(worker.id, set())
                for shift in worker.schedule:
                    key = f"{shift.begin.isoformat()}_{shift.end.isoformat()}_{getattr(shift.place, 'name', shift.place)}"
                    if key in w_cache:
                        bonus += 100.0
        
        score = total_penalty - bonus
        if score < 0:
            score = 0.0
            
        return 1.0 / (float(score) + 0.001)
    
    def createPlan(self):
        self.defaultPlaceSchedule(self.year, self.month)
        self.availability_cache.clear()
        
        for worker in self.workers:
            self.defaultRequestedSchedule(worker, self.year, self.month) 
            self.availability_cache[worker.id] = {
                f"{s.begin.isoformat()}_{s.end.isoformat()}_{getattr(s.place, 'name', s.place)}" 
                for s in worker.rqSchedule
            }

        custom_gene_space = self.converter.prepare_slots(self.month, self.year, self.availability_cache)
        num_genes: int = len(self.converter.ordered_slots)
        self.created_month = self.month

       
        ga_instance = pygad.GA(
            num_generations=400,                 # liczba pokolen
            sol_per_pop=100,                     # roznorodnosc genetyczna w populacji
            num_parents_mating=30,               # ilosc rodzicow do krzyzowania
            fitness_func=self.fitness_func,
            num_genes=num_genes,
            gene_space=custom_gene_space,
            on_generation=self.on_generation,
            
            # selekcja turniejowa
            parent_selection_type="tournament",
            K_tournament=4,                      # rozmiar turnieju
            
            # Zaawansowane dwupunktowe krzyżowanie 
            crossover_type="two_points",
            
           
            mutation_percent_genes=5,            
            mutation_type="random",       
            keep_elitism=5                       # zachowujemy 5 najlepszych osobnikow
        )
        
        print(f"[GA] Start zoptymalizowanej ewolucji (Slotow: {num_genes})...")
        ga_instance.run()
        
        solution, fitness, idx = ga_instance.best_solution()
        self.converter.update_all_objects_from_vector(solution)
        print(f"[GA] Zakonczono. Wynik Fitness: {fitness:.6f}")

        self.ready = 1
        return 1
    
    def on_generation(self, ga_instance):
        from PySide6.QtWidgets import QApplication
        QApplication.processEvents()
        print(f"Generation: {ga_instance.generations_completed} | Best Fitness: {ga_instance.best_solution()[1]:.6f}")