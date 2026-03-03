
from pathlib import Path
import json


class Saving():
    
    def __init__(self, workers_list, place_list, folder_name):

        self.workers_list = workers_list
        self.place_list = place_list
        #current path of code file
        current_path = Path(__file__).parent.resolve()
        self.saving_path = current_path / folder_name
        self.saving_path.mkdir(parents=False, exist_ok=True)

        self.workers_path = self.saving_path / "workers"
        self.workers_path.mkdir(parents=False, exist_ok=True)
        self.places_path = self.saving_path / "workplaces"
        self.places_path.mkdir(parents=False, exist_ok=True)

