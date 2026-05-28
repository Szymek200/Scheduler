from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from copy import deepcopy
from typing import Any, TYPE_CHECKING
from myExceptions import IntervalZero
import json



if TYPE_CHECKING:
    from shift import ShiftPlace
    from worker import Worker
    from place import Place

from constans import HARD_PENALTY, SOFT_PENALTY


class Rule(ABC):
    idBase: int = 0
    def __init__(self, name: str):
        self.id = Rule.idBase
        Rule.idBase += 1
        self.name = name
     
    @abstractmethod
    def serializer(self) -> dict[str, Any]:
        pass

    @classmethod
    def deserialize_rule(cls, rule_data: dict[str, Any], entity: Any)-> Rule | None:
        from worker import Worker
        from shift import ShiftPlace
        
        rule_type = rule_data.get("__type__")
        rule_name = rule_data.get("name", "Unnamed")
        rule_id = rule_data.get("id")
        
        # DEBUG: Zobaczymy co program widzi w pliku
        print(f"[LOADER] Trying to load rule: {rule_name} of type: {rule_type}")

        new_rule = None

        # Dopasowanie typów - upewnij się, że te stringi są identyczne jak w pliku JSON!
        if rule_type == "FreeWeekend":
            from rules.RightRules import FreeWeekend
            quantity = rule_data.get("quantity", 2)
            new_rule = FreeWeekend(entity, rule_name, quantity)

        elif rule_type == "BetweenShifts":
            from rules.RightRules import BetweenShifts
            val = rule_data.get("value", 39600)
            new_rule = BetweenShifts(entity, rule_name, timedelta(seconds=float(val)))

        elif rule_type == "CyclicRule":
            from rules.AvalRules import CyclicRule
            begin_data = rule_data.get("begin", {})
            interval_val = rule_data.get("interval", 1)
            try:
                # Zamieniamy słownik zmiany początkowej na tekst JSON i ładujemy deserializerem
                shift_json = json.dumps(begin_data)
                start_shift = ShiftPlace.deserializer(shift_json)
                
                # --- POPRAWIONO: Konwersja sekund z JSON na timedelta ---
                if float(interval_val) > 1000: # sekundy
                    delta = timedelta(seconds=float(interval_val))
                else: # dni (zabezpieczenie dla starych danych)
                    delta = timedelta(days=int(interval_val))
                    
                new_rule = CyclicRule(start_shift, delta, rule_name)
            except Exception as e:
                print(f"[LOADER ERROR] CyclicRule fail: {e}")

                
        elif rule_type in ["Etat Rule", "EtatRule"]:
            from rules.RightRules import EtatRule
            try:
                v = rule_data.get("value", 0)
                d = rule_data.get("deviation", 0)
                new_rule = EtatRule(entity, rule_name, timedelta(seconds=float(v)), timedelta(seconds=float(d)))
            except Exception as e:
                print(f"[LOADER ERROR] EtatRule fail: {e}")

        elif rule_type == "UnorderedRule":
        
            from rules.AvalRules import UnorderedRule
            from shift import ShiftPlace  
            try:
                decoded_shifts = []
                for shift_data in rule_data.get("shiftList", []):
                    # Zamieniamy słownik pojedynczej zmiany z powrotem na tekst JSON
                    shift_json = json.dumps(shift_data)
                    
                    # Wywołujemy Twój deserializer z ShiftPlace (przyjmuje tylko jeden argument!)
                    from_json_shift = ShiftPlace.deserializer(shift_json)
                    decoded_shifts.append(from_json_shift)
                
                # Tworzymy obiekt reguły UnorderedRule
                new_rule = UnorderedRule(shiftList=decoded_shifts, name=rule_name)
            except Exception as e:
                print(f"[LOADER ERROR] UnorderedRule fail: {e}")


        # Ustawianie ID reguły
        if new_rule:
            if rule_id is not None:
                new_rule.id = rule_id
            print(f"[LOADER] SUCCESS: Added {rule_name} to {entity.name}")
            return new_rule
        else:
            print(f"[LOADER WARNING] FAILED to recognize rule type: {rule_type}")
            return None