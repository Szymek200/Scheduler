

from datetime import timedelta, datetime
from itertools import combinations


from typing import Any, Optional, Self, TYPE_CHECKING

if TYPE_CHECKING:
    from rules import Rule, AvalRule, EtatRule
    from shift import ShiftPlace

class Worker:

    #class variable

    availableId: int = 1


    def __init__(self, name: str, surname: str, pesel: str):
        self.name = name
        self.surname = surname
        self.pesel = pesel

        self.id = self.availableId
        Worker.availableId += 1


        #is it necessary?
        #self.notEnoughHours = False

        #schedule that worker will actually work
        self.schedule: list[ShiftPlace] = []

        #requested schedule - created by AvalRules
        self.rqSchedule: list[ShiftPlace] = [] #



        self.rules: list[Rule] = []

        

    def serializer(self) -> dict[str, Any]:

        #we don't need to save schedules, just rules

        return{
            "__type__": "Worker",
            "name": self.name,
            "surname": self.surname,
            "pesel":self.pesel,
            "id":self.id,
            #"schedule": [shift.serializer() for shift in self.schedule],
            #serializer for every rule
            "rules":[rule.serializer() for rule in self.rules],
            #"rqSchedule":[shift.serializer() for shift in self.rqSchedule]
            
        }


    def addRequestedSchedule(self, rqSchedule: list[ShiftPlace]) -> None:

        #check if all shifts of worker calendar are ShiftPlace   

        if isinstance(rqSchedule, list) and all(isinstance(s, ShiftPlace) for s in rqSchedule):
            self.rqSchedule = rqSchedule

    def availableToday(self, date: datetime) -> bool:
        for shift in self.rqSchedule:
             if shift.begin.date() >= date and shift.end.date() <= date:
                    return True
        return False

    #checks every rule or rules of given class
    def compliesRules(self, shift: ShiftPlace, rule_class=None) -> bool:
        import rules
        
        # Jeśli jawnie wskazaliśmy, że chcemy sprawdzić konkretną klasę reguł (np. tylko AvalRule)
        if rule_class is not None:
            selected_rules = [r for r in self.rules if isinstance(r, rule_class)]
            
            # Jeśli szukamy reguł dostępności, a pracownik ich nie ma - domyślnie jest niedostępny
            # (lub True, jeśli wolisz, żeby domyślnie mógł pracować wszędzie)
            if rule_class == rules.AvalRule and not selected_rules:
                return False 
                
            # Dla reguł dostępności (AvalRule) - wystarczy, że JEDNA jest spełniona (logika OR)
            if rule_class == rules.AvalRule:
                for rule in selected_rules:
                    if rule.isFulfilled(shift):
                        return True
                return False
                
            # Dla innych reguł (np. RightRule) - wszystkie muszą być spełnione (logika AND)
            for rule in selected_rules:
                if not rule.isFulfilled(shift):
                    return False
            return True

        # --- DOMYŚLNA LOGIKA (gdy rule_class == None) ---
        # 1. RightRules (AND)
        worker_rules = [r for r in self.rules if isinstance(r, rules.RightRule)]
        for rule in worker_rules:
            if not rule.isFulfilled(shift):
                return False
                
        # 2. Availability rules (OR)
        availability_rules = [r for r in self.rules if isinstance(r, rules.AvalRule)]
        if not availability_rules:
            return True
            
        passed_any = False
        for rule in availability_rules:
            if rule.isFulfilled(shift):
                passed_any = True
                break
                
        return passed_any
    
    def addAcqShift(self, shift: ShiftPlace) -> None:
        self.schedule.append(shift)

    def addRule(self, rule) -> None:
        self.rules.append(rule)


    def removeRule(self, ruleId: int) -> bool:
        for rule in self.rules:
            if rule.id == ruleId:
                self.rules.remove(rule)
                return True
        return False

    #return first etat rule or None if there is no such rule
    def getEtatRule(self) -> Optional[EtatRule]:
        import rules
        for rule in self.rules:
            if isinstance(rule, EtatRule):
                return rule
        return None
        

    def howManyHours(self)-> timedelta:

        workingTime = timedelta(0)
        for shift in self.schedule:
            workingTime += shift.duration()
        return workingTime
        
    #retuns shifts he haas during this day
    def worksToday(self, date: datetime) -> list[ShiftPlace]: 
        shiftsToday = []
        for shift in self.schedule:
            if shift.begin.date() == date or shift.end.date() == date:
                shiftsToday.append(shift)
        return shiftsToday



    """
    #don't see point of this method    
    #how many hours maximum with rules it could work    
    def availability(self):

        #every place multiplies availability
        #we count hours not shifts!?!?!?
        maxHours = 0

        for i in range(len(self.rqSchedule)):
            #we take sum of shifts which do not overlap

            #NEED TO CHECK RULES FOR THESE SHIFTS!!!!!
            

            #availability = all hours, even if shifts overlap

            shiftCombinations = list(combinations(self.rqSchedule), i)

            #checking if combinations comly with rules

            if(self.complyWithRules(shiftCombinations)==1):
                if(utils.hoursSum(shiftCombinations) > maxHours):
                    maxHours = utils.hoursSum(shiftCombinations)

        return maxHours
    """


