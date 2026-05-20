from __future__ import annotations

from calendar import month
from datetime import datetime, time, timedelta

from baseScheduler import BaseScheduler
from rules import RightRule, AvalRule

from worker import Worker
from place import Place
from shift import ShiftPlace

from constans import HARD_PENALTY, SOFT_PENALTY

from ga_converter import GAConverter
import pygad



class GeneticScheduler(BaseScheduler):

    def __init__(self, workers: list[Worker], places: list[Place], month: int, year: int):
        self.workers = workers
        self.places = places
        self.month = month
        self.year = year

        self.converter = GAConverter(workers, places);

        print(f"[GA] Przygotowuje dane dla {len(self.workers)} pracownikow...")

        # Szybki słownik dostepnosci
        #klucz - worker id
        #wartosc - wszystkie zmiany w formacie tekstowym
        self.availability_cache = {} 
        

        #creating defalut schedule for every workers
        for worker in self.workers:
            self.defaultRequestedSchedule(worker, self.year, self.month) #empty shifts
            # Tworzymy zestaw unikalnych kluczy (data+godzina_beg+godzina_end+miejsce) dla błyskawicznego sprawdzania
            # zbior jest implementowany poprzez hash table


            #slownik z klucz - id pracownika
            #wartosc - zbior wszystkich zmian w miesiacu
            self.availability_cache[worker.id] = {
                f"{s.begin.isoformat()}_{s.end.isoformat()}_{getattr(s.place, 'name', s.place)}" 
                for s in worker.rqSchedule
            }
          
      
    def hard_rules(self) -> float:

        worker_map = {w.id: w for w in self.workers}

        penalty:float = 0.0
 
        for worker in self.workers:
            
            w_rules = [rule for rule in worker.rules if isinstance(rule, RightRule)]

            for rule in w_rules:
                        if isinstance(rule, RightRule):
                            penalty += rule.completion(worker)
       
        return penalty
    
    def fitness_func(self, ga_instance, solution, solution_idx):
        # 1. Update obiektow (to musi byc, ale robimy to raz na osobnika)
        self.converter.update_objects_from_vector(solution)
        
        penalty = 0
        # 2. Kara za puste sloty (bardzo wysoka)
        penalty += self.converter.get_invalid_slots_count() * 1000
        
        penalty += self.hard_rules()
     

        return 1.0 / (penalty + 0.001)
    

    def createPlan(self, month: int, year: int):
        # --- TRYB TESTOWY: Male wartosci, zeby sprawdzic czy dziala ---
        custom_gene_space = self.converter.prepare_slots(month, year, self.availability_cache)

        num_genes:int = len(self.converter.ordered_slots)

        ga_instance = pygad.GA(
            num_generations=20,           # Tylko 20 pokolen na start
            num_parents_mating=5,
            fitness_func=self.fitness_func,
            sol_per_pop=20,               # Tylko 20 osobnikow
            num_genes=num_genes,
            gene_space=custom_gene_space,
            on_generation=self.on_generation, # Widzisz postep w konsoli!
            mutation_percent_genes=5
        )
        
        print(f"[GA] Start ewolucji (Slotow: {num_genes})...")
        ga_instance.run()
        
        solution, fitness, idx = ga_instance.best_solution()
        self.converter.update_all_objects_from_vector(solution)
        print(f"[GA] Zakonczono. Wynik: {fitness:.6f}")
        return solution
    
    def on_generation(ga_instance):
        print("Generation : ", ga_instance.generations_completed)
        print("Fitness of the best solution :", ga_instance.best_solution()[1])