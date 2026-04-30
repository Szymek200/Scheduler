from pathlib import Path
import json

# Musimy zaimportować klasy, żeby deserializator wiedział, jak je odtworzyć
from worker import Worker
from place import Place
import rules
from shift import ShiftPlace
from datetime import datetime

class Saving():
    
    def __init__(self, workers_list, place_list, folder_name):
        self.workers_list = workers_list
        self.place_list = place_list
        self.folder_name = folder_name
        current_path = Path(__file__).parent.resolve()
        self.saving_path = current_path / folder_name
        self.saving_path.mkdir(parents=False, exist_ok=True)

        # Dodano rozszerzenia .json dla poprawności plików
        self.workers_path = self.saving_path / "workers.json"
        self.places_path = self.saving_path / "workplaces.json"

    def saving(self):        
        with open(self.workers_path, "w", encoding="utf-8") as file:
            # Tworzymy tablicę słowników i zapisujemy ją raz
            serialized_workers = [worker.serializer() for worker in self.workers_list]
            json.dump(serialized_workers, file, indent=4)

        with open(self.places_path, "w", encoding="utf-8") as file:
            serialized_places = [place.serializer() for place in self.place_list]
            json.dump(serialized_places, file, indent=4)


    def reading(self):
        current_path = Path(__file__).parent.resolve()
        saving_path = current_path / self.folder_name
        workers_path = saving_path / "workers.json"
        places_path = saving_path / "workplaces.json"

        loaded_workers = []
        loaded_places = []

     
        if workers_path.exists():
            with open(workers_path, "r", encoding="utf-8") as file:
                try:
                    workers_data = json.load(file) 
                except json.JSONDecodeError:
                    workers_data = [] # W przypadku błędu JSON zacznij od pustej listy
                
                for item in workers_data:
                    if item.get("__type__") == "Worker":
                        worker = Worker(item["name"], item["surname"], item["pesel"])
                        worker.id = item["id"] 
                        
                        
                        if "rules" in item:
                            for rule_data in item["rules"]:
                                new_rule = rules.deserialize_rule(rule_data, worker)
                                if new_rule:
                                    worker.addRule(new_rule)

                        loaded_workers.append(worker)

      
        if places_path.exists():
            with open(places_path, "r", encoding="utf-8") as file:
                try:
                    places_data = json.load(file)
                except json.JSONDecodeError:
                    places_data = [] 
                    
                for item in places_data:
                    if item.get("__type__") == "Place":
                        place = Place(item["name"], item["address"])
                        place.id = item["id"] 
                        
                        
                        if "rules" in item:
                            for rule_data in item["rules"]:
                                new_rule = rules.deserialize_rule(rule_data, place)
                                if new_rule:
                                    place.addRule(new_rule)

                        loaded_places.append(place)

        return loaded_workers, loaded_places