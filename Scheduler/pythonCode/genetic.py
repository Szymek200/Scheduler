import pygad
import numpy

from pythonCode.baseScheduler import BaseScheduler  

class GenSchedueler(BaseScheduler):
    def __init__(self, workers, places, num_generations=50, num_parents_mating=4, sol_per_pop=8):

        super().__init__(workers, places)

        self.num_generations = num_generations
        self.num_parents_mating = num_parents_mating
        self.sol_per_pop = sol_per_pop

        #all shifts that need to be filled - from place perspective
        self.emptyShifts = []



    def createPlan(self, month, year):

        #PREPARING DATA FOR GENETIC ALGORITHM

        #PREPARING EMPTY SHIFTS

        self.defaultPlaceSchedule(year, month)

        #cleaning old data
        for worker in self.workers:
            worker.acquiredSchedule.clear()
            self.defaultSchedule(worker, year, month)

        self.sort_workers_by_id()
          
   

        for place in self.places:
            self.emptyShifts.extend(place.schedule)

       
        function_inputs = np.array(len(emptyShifts))  # Example input data for the fitness function


    
        #GENETIC ALGORITHM

        #Configure the Genetic Algorithm
        ga_instance = pygad.GA(
            num_generations=50,
            num_parents_mating=4,   #how many individuals from the current population are selected as parents to produce the next generation
            fitness_func=fitness_func,
            sol_per_pop=8,  #number of solutions in each generation
            num_genes=len(function_inputs),
            gene_space={'low': min(self.workers.id), 'high': max(self.workers.id)} # Range for the weights
        )

        # 4. Run the Evolution
        ga_instance.run()

        # 5. Extract the results
        solution, solution_fitness, solution_idx = ga_instance.best_solution()
        print(f"Parameters of the best solution : {solution}")
        print(f"Fitness value of the best solution = {solution_fitness}")

        # Visualize the progress
        ga_instance.plot_fitness()

    
    def sort_workers_by_id(self):
        self.workers.sort(key=lambda worker: worker.id)

   
def fitness_func(self, ga_instance, solution, solution_idx):
    # 1. Reset current state for this evaluation
    # We must clear previous assignments to calculate this specific solution's validity
    for worker in self.workers:
        worker.acquiredSchedule = []

    # Map workers by ID for quick lookup (since solution contains IDs)
    worker_map = {w.id: w for w in self.workers}

    # 2. Assign workers to shifts based on the GA solution
    for i, worker_id in enumerate(solution):
        # Cast to int as GA might pass floats depending on configuration
        w_id = int(worker_id)
        worker = worker_map.get(w_id)
        
        if worker:
            shift = self.emptyShifts[i]
            # Link the worker to the shift and vice versa
            shift.worker = worker
            worker.addWorkerShift(shift)

    hard_rules_broken = 0
    soft_rules_broken = 0

    # 3. Validate Rules for every shift/worker
    for shift in self.emptyShifts:
        worker = shift.worker
        place = shift.place

        # --- Validate Place Rules ---
        # According to your logic: "other rules" = Hard
        for rule in place.rules:
            if not rule.isFulfilled(shift):
                hard_rules_broken += 1

        # --- Validate Worker Rules & Availability ---
        # Separate logic for WorkerRule (Soft) and availability Rule (Hard)
        has_availability_rules = False
        satisfied_any_availability = False

        for rule in worker.rules:
            # Rule (Availability like CyclicRule/UnorderedRule) -> Hard (OR logic)
            if isinstance(rule, Rule):
                has_availability_rules = True
                if rule.isFulfilled(shift):
                    satisfied_any_availability = True
            
            # WorkerRule (BHP like EtatRule/FreeWeekend) -> Soft (AND logic)
            elif isinstance(rule, WorkerRule):
                if not rule.isFulfilled(shift):
                    soft_rules_broken += 1

        # If worker has availability rules but none matched this shift -> Hard broken
        if has_availability_rules and not satisfied_any_availability:
            hard_rules_broken += 1

    # 4. Calculate Final Fitness Score
    # We want to maximize this value. 
    # Hard rules are weighted heavily so any solution breaking a hard rule 
    # is significantly worse than one only breaking soft rules.
    # Adding 0.000001 prevents division by zero.
    fitness = 1.0 / (1.0 + (hard_rules_broken * 1000) + soft_rules_broken)
    
    return fitness