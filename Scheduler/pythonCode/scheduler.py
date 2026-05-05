from pythonCode.baseScheduler import BaseScheduler
from worker import Worker
from place import Place
from shift import ShiftPlace
from itertools import product
from datetime import datetime, time, timedelta
from itertools import combinations
from dataclasses import dataclass, field
import copy
import utils

from rules import *

#for rotation purposes
@dataclass #automatically creates init and rept methods
class WorkerData:
    worker: Worker        # Your Worker object
    Hours: float          # hours worker will lose if we transfer him to this shift

    #generates new list for every class object
    list: list = field(default_factory=list) # List of ShiftPlace objects

class Scheduler(BaseScheduler):
    def __init__(self, workers, places):
        super().__init__(workers, places)

        #default value - 0
        #returns availability
        self.availability = [0] * len(workers)
        self.availabilityrequiredHours = [0] * len(workers)


        #zip arrays together
        #workers, self.availability, self.requiredHours

        
    #sort workers on how many shifts they can take in relation to his demands(hours he needs to work)    
    def availability(self):
        size = len(self.workers)

        for i in range(size):
            worker = self.workers[i]
            total_available_time = timedelta(0)

        
            #sum of hours from every shift
            for shift in worker.rqSchedule:
                # ShiftPlace has one place
                total_available_time += shift.duration()
            
          
            etat_rule = worker.getEtatRule()
            
            if etat_rule and etat_rule.value.total_seconds() > 0:
                # convert values to seconds
                self.availability[i] = total_available_time.total_seconds() / etat_rule.value.total_seconds()
            else:
                # if worker doesn't have etat - works errands = 0
                self.availability[i] = 0.0
    

    #substitude comply with rules

    def substitudeCompliance(self, shiftOne, rulesTypes):

        #we check 2 shifts
        #first shift is for substitution guy - only rulesTypes

        #substitution shift
        #shift inside has every required info
        if shiftOne.place.compliesRules(shiftOne):
            for rule in  shiftOne.worker.rules:
                #if that rule is chosen to check
                for type in rulesTypes:
                    if rule.rule_type == type:
                        if not rule.isFulfilled(shiftOne):
                            return False
                        break

        
        return True

        
    
    #we add shift without worker and automatically ads and deletes if unsucessfull

    #container for comply with rules
    def checkCompliance(self, shift, worker):
            

            oldWorker = shift.worker

            shift.worker = worker

            is_compliant = self.complyWithRules(shift)

            shift.worker = oldWorker

            #we are only checking - not applying changes
            return is_compliant

            """
            if self.complyWithRules(shift):
                #it should because this does first stage
                worker.addWorkerShift(shift)
                return True
            else:
                shift.worker = oldWorker
                return False
            """



    #check requirements
    #if there is enough workers and shifts to work
    def schedulePossible(self):
        return True
         
        placeHours = timedelta(0)

        for place in self.places:
            for shift in place.schedule:
                placeHours += shift.duration

        #etat workers hours

        etatWorkersHours = timedelta(0)
        nonEtatHours = timedelta(0)
        for worker in self.workers:

            if worker.etat == 0:
                nonEtatHours += timedelta(hours = worker.availability())
                
            else:
                etatWorkersHours += timedelta(hours=worker.etat)

        #all etat workers will work
        if(placeHours < etatWorkersHours):
            return False
        
        #we can fill all gaps with errand workers
        if placeHours > etatWorkersHours and placeHours - etatWorkersHours < nonEtatHours:
            return True

        return False 
    
    def createPlan(self, month, year):
        self.ready = False
        if self.schedulePossible() == False:
            return 
        
        #cleaning old data
        for worker in self.workers:
            worker.acquiredSchedule.clear()
            self.defaultSchedule(worker, year, month)
          
        emptyShifts = []

        for place in self.places:
            emptyShifts.extend(place.schedule)

        #sort shift by least available workers for this shift
        shiftDemand = [0] * len(emptyShifts)
        
        #pointers to workers for particular shift
        #I create sublist for every elem
        workerPointers = [[] for _ in range(len(emptyShifts))]

        for index, shift in enumerate(emptyShifts):
            for worker in self.workers:
                if worker.availableToday(shift):
                    shiftDemand[index] += 1
                    workerPointers[index].append(worker) 

        #sort shifts by demands
        #default - ascending
        sorted_shifts = sorted(zip(emptyShifts,shiftDemand, workerPointers), key=lambda x: x[1])

        #* - pours lists into separate ones

        #good way
        emptyShifts, shiftDemand, workerPointers = map(list, zip(*sorted_shifts))
        #wrong way
        #emptyShifts, shiftDemand, workerPointers = zip(*sorted_shifts)


        #shifts which noone gave availability
        i = 0
        orphans = []
        while len(shiftDemand) > 0 and shiftDemand[0] == 0:
            orphans.append(emptyShifts[0])
            emptyShifts.pop(0)
            shiftDemand.pop(0)
            workerPointers.pop(0)

        #every shift has at least one worker
        for index, shift in enumerate(emptyShifts):
             #chose worker with least fullfilled etat
             #worker and fraction of etat
            sortedWorkers = []
            
            for worker in workerPointers[index]:
                # ZMIANA: Sortujemy po ilości przepracowanego już czasu!
                sortedWorkers.append((worker, worker.howManyHours()))

            sortedWorkers.sort(key=lambda pair: pair[1])
            found = False
            for worker_pair in sortedWorkers:
                real_worker = worker_pair[0]
                shift.worker = real_worker # Przymiarka
                
                if self.complyWithRules(shift):
                    print(f"✅ OK: {real_worker.name} przypisany do {shift.begin} ({shift.place.name})")
                    real_worker.addWorkerShift(shift)
                    found = True
                    break
                else:
                    # To powie Ci, który pracownik został odrzucony
                    print(f"❌ ODRZUCONO: {real_worker.name} nie spełnia reguł dla {shift.begin}")
                    shift.worker = None
            
            if not found:
                print(f"⚠️ ALARM: Nikt nie może pracować na zmianie {shift.begin} w {shift.place.name}!")

        self.ready = True
    



    
    #returns list of people who could have work this shift
    #but currently can't because of other shifts
    #and how many shifts we would delete by switching worker to it
    def whoCanWorkToday(self, argShift):

        result = []

        for worker in self.workers:
            for shift in worker.rqschedule:
                if shift.sameShift(argShift):

                    #how many shifts he will lose by this transfer
                    #how to do it better than checking all schedule!!?!?!?!?!?!?!!??

                    colisionShifts = []

                    #shift has worker that we transfer
                    for rule in shift.worker.rules:
                        #extend in different to append that extent argument list pushes as individual objects
                        colisionShifts.extend(rule.uncompliedShift(shift))

                    lostHours = timedelta(0)
                    for shift in colisionShifts:
                        lostHours += shift.duration()

                    result.append(WorkerData(worker, lostHours, colisionShifts))

        result.sort(key=lambda x: x.lostHours)

        return result

    #returns guy who could substiute this shift with all rules applied
    def findSubstitution(self, shift):
        for worker in self.workers:

            #rqShift - zmiana u innego pracownika, ktory teoretycznie moze wtedy pracowac
            #ale trzeba sprawdzic reguly
            for rqShift in worker.rqSchedule:
                #he may work
                if rqShift.sameShift(shift):
                        #he complies with the rules
                        
                    if worker.compliesRules(shift) and rqShift.place.compliesRules(rqShift):
                        return worker

        return -1

  

    #priority for rotations
    def workerPriority(self, worker):
        rule = worker.getEtatRule()

        if rule:
            if not rule.isComplete():
                return 0
            else:
                return 2 #overtime
        else:
            return 1

    #move shifts because at first round we weren't able to fill all shifts
    def rotations(self):

        #repetition from createPlan

        emptyShifts = []

        for place in self.places:

            for shift in place.schedule:
                if shift.worker == None:
                    emptyShifts.append(shift)

        #sort shift by least available workers for this shift
        shiftDemand = [0] * len(emptyShifts)
        
        #pointers to workers for particular shift
        #I create sublist for every elem
        workerPointers = [[] for _ in range(len(emptyShifts))]

        for index, shift in enumerate(emptyShifts):
            for worker in self.workers:
                if worker.availableToday(shift):
                    shiftDemand[index] += 1
                    workerPointers[index].append(worker) 

        #sort shifts by demands
        #default - ascending
        sorted_shifts = sorted(zip(emptyShifts,shiftDemand, workerPointers), key=lambda x: x[1])

        #* - pours lists into separate ones
       # emptyShifts, shiftDemand, workerPointers = zip(*sorted_shifts)


        #begin rotations from shift with least worker availability

        for index in range(len(sorted_shifts)):
            newGuyFound = False

            #sort workers - first with not enough hours in etat

            sorted_shifts[index][2].sort(key=self.workerPriority)            

            #go through workerPointers
            for importWorker in sorted_shifts[index][2]:

                #import worker - the guy who can work that shift but rules don't allow
                #reduced rules
                #issue with different duration of exchagne shifts

                rulesTypes = ["free weekend", "between shifts"]

                if self.substitudeCompliance( sorted_shifts[index][0], rulesTypes):

                    #list of all workers with not enough work hours
                    lessEtat = []

                    noEtat = []
                    lackEtat = []
                    for worker in self.workers:
                        
                        existingRule = worker.getEtatRule()


                        if existingRule:
                            if not existingRule.isComplete():
                                lackEtat.append(worker)
                        else:
                            noEtat.append(worker)

                    lessEtat = lackEtat + noEtat
                    
                        


                        

                    #find new guy for other import worker shift

                    #to do - it would be better to check first for collisions around added shift!!!!!
                    #to do - remember exchages to stop echange loop

                    for shift in importWorker.acquiredSchedule:
                        # we check if new guy can work here
                        for newGuy in lessEtat:
                            for rqShift in newGuy.rqSchedule:
                                if shift.sameShift(rqShift) and self.checkCompliance( shift, newGuy):
                                     

                                    #now we need to check is exchange did resolve issue with import Guy
                                    
                                    importWorker.acquiredSchedule.remove(shift)

                                    #this is ok
                                    shift.worker = newGuy
                                    newGuy.addWorkerShift(shift)
                                    

                                    #we check if this below is ok
                                

                                    if self.checkCompliance(sorted_shifts[index][0], importWorker):
                                        #it should because this does first stage

                                        #is it necessary here???
                                        sorted_shifts[index][0].worker = importWorker
                                        importWorker.addWorkerShift(sorted_shifts[index][0])

                             
                                        #we check if the newGuy is still available for other shifts to take
                                        existingRule = newGuy.getEtatRule()
                                        if existingRule and existingRule.isComplete():
                                            lessEtat.remove(newGuy)

                                        newGuyFound = True

                                        break
                                    else:

                                        newGuy.acquiredSchedule.remove(shift)
                                        shift.worker = importWorker #odl worker, which was before
                                        importWorker.addWorkerShift(shift)


                                        
                                       

                                        
                            
                            if(newGuyFound):
                                break

                if newGuyFound:
                    break      
                           
    

    def ErrandWorkers(self):

        errandWorkers = []
        for worker in self.workers:
            errandWorkers.append(worker)

        emptyShifts = []

        for place in self.places:
            
            for shift in place.schedule:
                if shift.worker == None:
                    emptyShifts.append(shift)

        #variation with repetiton

        shiftVarations = list(product(errandWorkers, repeat=len(emptyShifts)))

        for varation in shiftVarations:
            #we check if all rules are followed

            correct = True

            for i in range(len(emptyShifts)):
                
                tryShift: ShiftPlace = copy.deepcopy(emptyShifts[i])
                tryShift.worker = varation[i]

                if not (varation[i].compliesRules(tryShift) and tryShift.place.compliesRules(tryShift, varation[i])):
                    correct = False

            

            if correct == True:
                #this variation is ok - we apply it

                # we can enlarge this mechanism by selecting better variation

                 for i in range(len(emptyShifts)):
                     emptyShifts[i].worker = varation[i]
                 return 0
        return -1
                    
    









