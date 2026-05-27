from __future__ import annotations


import json
from typing import Any, Self, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from rules import Rule
from shift import ShiftPlace


class Place:

    #class variable

    availableId: int = 1


    def __init__(self, name:str, address: str):
        self.name: str = name
        self.address: str = address
        self.id: int = self.availableId

        self.availableId += 1
        self.rules: list['Rule'] = []
        self.schedule: list[ShiftPlace] = []

    

        

    def addRequestedSchedule(self, rqSchedule: list[ShiftPlace]) -> None:

        if isinstance(rqSchedule, list):
            self.schedule = rqSchedule
    
    def compliesRules(self, shift: ShiftPlace, worker=None) -> bool:
            import rules
       
            #rules specyfic for this particular place - RulePlace - all at once need to be fullfilled
            place_rules: list[rules.RightRule] = [r for r in self.rules if isinstance(r, rules.RightRule)]
            for rule in place_rules:
                if not rule.isFulfilled(shift):
                    return False
                    
         
            #availability rules - for example Cyclic rule - OR
            availability_rules: list[rules.AvalRule] = [r for r in self.rules if isinstance(r, rules.AvalRule)]
            if availability_rules:
                passed_any = False
                for rule in availability_rules:
                    if rule.isFulfilled(shift):
                        passed_any = True
                        break
                
                #if we didn't find any complied rule -> false
                if not passed_any:
                    return False
                    
            return True
    
    def addRule(self, rule) -> None:
        import rules
        if isinstance(rule, rules.Rule):
            self.rules.append(rule)

    def addShift(self, shift: ShiftPlace):
        if shift not in self.schedule:
            self.schedule.append(shift)

    def availableShift(self, argShift: ShiftPlace) -> bool:
        for shift in self.schedule:
            #we need cast because generally there is worker 
            if shift.sameShift(argShift):
                return True
        return False

    #we add worker to the shift

    #is there better way to do it?
    def addWorkerToShift(self, argShift: ShiftPlace) -> None:
        for shift in self.schedule:
            #we need cast because generally there is worker 
            if shift.sameShift(argShift):
                #will it change value on the list?
                shift = argShift
                break

    def allShiftsOccupied(self) -> bool:
        self.schedule.sort(key=lambda x: (x.worker is not None, x.begin))
        if self.schedule[0].worker == None:
            return False
        return True
    

    def serializer(self) -> dict[str, Any]:
        return{
            "__type__": "Place",
            "name": self.name,
            "address":self.address,
            "id":self.id,
            "rules":[rule.serializer() for rule in self.rules],
            #"schedule":self.schedule
            
        }   