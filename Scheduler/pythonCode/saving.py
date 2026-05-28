from pathlib import Path
import json


import rules
from worker import Worker
from place import Place
from rules import Rule
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

        self.workers_path = self.saving_path / "workers.json"
        self.places_path = self.saving_path / "workplaces.json"

    def saving(self):        
        try:
            # 1. NAJPIERW przygotowujemy tekst JSON w pamięci RAM.
            # Jeśli tu wyskoczy jakikolwiek błąd (np. AttributeError), pętla się przerwie,
            # ale plik workers.json na dysku będzie w 100% bezpieczny i nienaruszony!
            serialized_workers = [worker.serializer() for worker in self.workers_list]
            workers_json_data = json.dumps(serialized_workers, indent=4)
            
            # 2. DOPIERO po pełnym sukcesie otwieramy plik i go nadpisujemy
            with open(self.workers_path, "w", encoding="utf-8") as file:
                file.write(workers_json_data)
                
            print("[SAVER] Pomyślnie zapisano plik workers.json")
            
        except Exception as e:
            print(f"[CRITICAL SAVER ERROR] Nie nadpisano pliku workers.json z powodu błędu: {e}")
            # Wyświetlamy pełny traceback w konsoli, żebyś widział gdzie dokładnie tkwi problem
            import traceback
            traceback.print_exc()

        try:
            # To samo bezpieczeństwo dla miejsc pracy (workplaces.json)
            serialized_places = [place.serializer() for place in self.place_list]
            places_json_data = json.dumps(serialized_places, indent=4)
            
            with open(self.places_path, "w", encoding="utf-8") as file:
                file.write(places_json_data)
                
            print("[SAVER] Pomyślnie zapisano plik workplaces.json")
            
        except Exception as e:
            print(f"[CRITICAL SAVER ERROR] Nie nadpisano pliku workplaces.json z powodu błędu: {e}")
            import traceback
            traceback.print_exc()

    def reading(self):
        current_path = Path(__file__).parent.resolve()
        saving_path = current_path / self.folder_name
        workers_path = saving_path / "workers.json"
        places_path = saving_path / "workplaces.json"

        self.workers_list.clear()
        self.place_list.clear()

        # 1. NAJPIERW WCZYTUJEMY MIEJSCA (żeby mieć bazę do mapowania)
        if places_path.exists():
            with open(places_path, "r", encoding="utf-8") as file:
                try: places_data = json.load(file)
                except json.JSONDecodeError: places_data = [] 
                    
                for item in places_data:
                    if item.get("__type__") == "Place":
                        place = Place(item["name"], item["address"])
                        place.id = item["id"] 
                        self.place_list.append(place)

        # 2. NASTĘPNIE WCZYTUJEMY PRACOWNIKÓW
        if workers_path.exists():
            with open(workers_path, "r", encoding="utf-8") as file:
                try: workers_data = json.load(file) 
                except json.JSONDecodeError: workers_data = []
                
                for item in workers_data:
                    if item.get("__type__") == "Worker":
                        worker = Worker(item["name"], item["surname"], item["pesel"])
                        worker.id = item["id"] 
                        self.workers_list.append(worker)

        # 3. DOPIERO TERAZ WCZYTUJEMY REGUŁY I ŁĄCZYMY JE Z OBIEKTAMI (RELACJE)
        # Przechodzimy ponownie przez surowe dane JSON, by zbudować reguły mając komplet obiektów w pamięci RAM
        
        # Odtwarzanie reguł dla Miejsc Pracy
        if places_path.exists() and places_data:
            for item, place_obj in zip(places_data, self.place_list):
                if "rules" in item:
                    for rule_data in item["rules"]:
                        new_rule = Rule.deserialize_rule(rule_data, place_obj)
                        if new_rule:
                            if hasattr(new_rule, 'owner'): new_rule.owner = place_obj
                            self._resolve_rule_references(new_rule)
                            place_obj.addRule(new_rule)

        # Odtwarzanie reguł dla Pracowników
        if workers_path.exists() and workers_data:
            for item, worker_obj in zip(workers_data, self.workers_list):
                if "rules" in item:
                    for rule_data in item["rules"]:
                        new_rule = Rule.deserialize_rule(rule_data, worker_obj)
                        if new_rule:
                            if hasattr(new_rule, 'owner'): new_rule.owner = worker_obj
                            self._resolve_rule_references(new_rule)
                            worker_obj.addRule(new_rule)

        return self.workers_list, self.place_list

    def _resolve_rule_references(self, rule):
        """Pomocnicza metoda wiążąca luźne ID wewnątrz reguł z obiektami z bazy danych."""
        # 1. Obsługa reguły cyklicznej i innych reguł posiadających obiekt ShiftPlace w pamięci
        if hasattr(rule, 'begin') and rule.begin is not None:
            self._link_shift_to_objects(rule.begin)
            
        # 2. Obsługa reguły z listą zmian (UnorderedRule)
        if hasattr(rule, 'shiftList') and rule.shiftList:
            for shift in rule.shiftList:
                self._link_shift_to_objects(shift)

    def _link_shift_to_objects(self, shift):
        """Zamienia tekstową nazwę miejsca i int worker_id w ShiftPlace na prawdziwe obiekty."""
        # Łączenie miejsca po nazwie
        if isinstance(shift.place, str):
            actual_place = next((p for p in self.place_list if p.name == shift.place), None)
            if actual_place:
                shift.place = actual_place

        # Łączenie pracownika po ID
        if isinstance(shift.worker, int) or (isinstance(shift.worker, str) and shift.worker.isdigit()):
            w_id = int(shift.worker)
            actual_worker = next((w for w in self.workers_list if w.id == w_id), None)
            if actual_worker:
                shift.worker = actual_worker