from pathlib import Path
import json

# Musimy zaimportować klasy, żeby deserializator wiedział, jak je odtworzyć
from worker import Worker
from place import Place
import rules
from shift import ShiftPlace

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

        
      # 1. Odczyt Pracowników
        if workers_path.exists():
            with open(workers_path, "r", encoding="utf-8") as file:
                workers_data = json.load(file) 
                
                for item in workers_data:
                    if item.get("__type__") == "Worker":
                        # worker
                        worker = Worker(item["name"], item["surname"], item["pesel"], item.get("etat", 0))
                        worker.id = item["id"] 
                        
                        # ODTWARZANIE REGUŁ
                        if "rules" in item:
                            for rule_data in item["rules"]:
                                rule_type = rule_data.get("__type__")
                                rule_name = rule_data.get("name", "")
                                
                                #creating correct rule according to "__type__"
                                if rule_type == "FreeWeekend":
                                    # Zauważ, że przekazujemy nowo stworzonego worker'a!
                                    new_rule = rules.FreeWeekend(worker, rule_name)
                                    new_rule.id = rule_data.get("id", new_rule.id)
                                    worker.addRule(new_rule)
                                    
                                elif rule_type == "BetweenShifts":
                                    new_rule = rules.BetweenShifts(worker, rule_name)
                                    new_rule.id = rule_data.get("id", new_rule.id)
                                    worker.addRule(new_rule)
                                    
                                elif rule_type == "UnorderedRule":
                                    # Ta reguła ma w sobie listę zmian (shiftów), musimy je odtworzyć
                                    shifts_array = []
                                    for s_data in rule_data.get("shiftList", []):
                                        # Zwróć uwagę, jak wyciągamy dane shifta z JSONa
                                        shift = ShiftPlace(s_data["begin"], s_data["end"], s_data.get("place", ""), worker)
                                        shifts_array.append(shift)
                                        
                                    new_rule = rules.UnorderedRule(shifts_array, rule_name)
                                    new_rule.id = rule_data.get("id", new_rule.id)
                                    worker.addRule(new_rule)

                        loaded_workers.append(worker)

        if places_path.exists():
            with open(places_path, "r", encoding="utf-8") as file:
                places_data = json.load(file)
                for item in places_data:
                    if item.get("__type__") == "Place":
                            # place
                            place = Place(item["name"], item["address"])
                            place.id = item["id"] 
                            
                            # ODTWARZANIE REGUŁ
                            if "rules" in item:
                                for rule_data in item["rules"]:
                                    rule_type = rule_data.get("__type__")
                                    rule_name = rule_data.get("name", "")
                                    
                                    #creating correct rule according to "__type__"
                                    if rule_type == "CyclicRule":
                                        begin = rule_data["begin"]
                                        interval= rule_data["interval"]
                                        new_rule = rules.CyclicRule(begin, interval, rule_name)

                               
                              

                loaded_places.append(place)

        return loaded_workers, loaded_places