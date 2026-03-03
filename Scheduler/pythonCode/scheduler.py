from worker import Worker
from place import Place
from shift import ShiftPlace
from itertools import product
from datetime import datetime, time, timedelta
from itertools import combinations
from dataclasses import dataclass, field
import copy
import utils

#for rotation purposes
@dataclass #automatically creates init and rept methods
class WorkerData:
    worker: Worker        # Your Worker object
    Hours: float          # hours worker will lose if we transfer him to this shift

    #generates new list for every class object
    list: list = field(default_factory=list) # List of ShiftPlace objects

class Scheduler:
    def __init__(self, workers, places):
        #workers have requested schedule and its requirements
        #places have required shifts to fill
        
        if not (isinstance(workers, list) and all(isinstance(item, Worker) for item in workers)):
            return -1

        if not (isinstance(places, list) and all(isinstance(item, Place) for item in places)):
            return -1
        
        
        self.places = places
        self.workers = workers
            #default value - 0
        #returns availability
        self.availability = [0] * len(workers)
        self.availabilityrequiredHours = [0] * len(workers)

        #zip arrays together
        #workers, self.availability, self.requiredHours

        
    #sort workers on how many shifts they can take in relation to his demands(hours he needs to work)    
    def availability(self):

        #every place multiplies availability
        #we count hours not shifts!?!?!?

        #everything is a reference

  

        #number of workers
        size = len(self.workers)

    

        for i in range(size):

            #if with shifts worker gave he can do required hours per month
            #we take sum of shifts which do not overlap

            #NEED TO CHECK RULES FOR THESE SHIFTS!!!!!
            enoughHours = 0

            #availability = all hours, even if shifts overlap

            for shift in self.workers.rqSchedule:
                
                
                for place in shift.places:
                    self.availability[i] += shift.duration()
            
            self.availability[i] /= self.workers[i].requiredHours()

#checks if worker gave enough availability to complete required hours
#max shift hours with shifts complying with Place Rules
#returns how much hours he can work with complying with the rules
    def requiredHours(self):

        for i in range(len(self.workers)):
             
             #we check every permutation that complies with the rules and take max

            maxHours = timedelta(0)

            for i in range(len(self.workers.rqSchedule)):
            #second argument - number of shifts is combination

                #I dont know if combinations argument is correct
                shiftCombinations = list(combinations(self.rqSchedule.shifts, i))

                #checking if combinations comly with rules

                if(self.complyWithRules(shiftCombinations)==1):
                    if(utils.hoursSum(shiftCombinations) > maxHours):
                        maxHours = utils.hoursSum(shiftCombinations)

            self.requiredHours[i] = maxHours
        
       
                    
                    
   

    #for every shift we check
    #place and worker rules
    def complyWithRules(self, shift):

        #check only one shift
        #shift inside has every required info
        if shift.place.compliesRules(shift) and shift.worker.compliesRules(shift):
            return True
        return False
    
    def schedulePossible(self):

         #check requirements
        #if there is enough workers and shifts to work
        placeHours = timedelta(0)

        for place in self.places:
            for shift in place.shedule:
                placeHours += shift.duration

        #etat workers hours

        etatWorkersHours = timedelta(0)
        nonEtatHours = 0
        for worker in self.workers:

            if worker.etat == 0:
                nonEtatHours += worker.availability()
                
            else:
                etatWorkersHours += worker.etat

        #all etat workers will work
        if(placeHours < etatWorkersHours):
            return False
        
        #we can fill all gaps with errand workers
        if placeHours > etatWorkersHours and placeHours - etatWorkersHours < nonEtatHours:
            return True

        return False 
        
    
    def createPlan(self):

       

        if self.schedulePossible() == False:
            return -1

        self.availability()
        #if everyone gave enough availability
        self.requiredHours()

        #sorting all lists for rising availability
        combined = list(zip(self.workers, self.availability, self.requiredHours))

        #sort by availability
        combined.sort(key=lambda x: x[1])

        #returns tuples
        w, a, r = zip(*combined)
        
        #back to lists
        self.workers, self.availability, self.requiredHours = list(w), list(a), list(r)

        #easy shedule
        #if all fit at first place - great

        #begin will least available worker
        for i in range(len(self.workers)):

            #in firsty round we skip non etat workers
            if self.workers[i].etat == 0:
                continue
            
            for avalShift in self.workers[i].rqSchedule:
                
                #if in place this shift is empty
                if avalShift.place.availableShift(avalShift):
                    #if all rules are complied with
                    if(avalShift.place.compliesRules(avalShift) and avalShift.worker.compliesRules(avalShift)):
                        avalShift.place.addWorkerShift(avalShift)
                        avalShift.worker.addWorkerShift(avalShift)
        
        
        #now check if all place shifts are filled and every worker has required hours

        #hours that worker needs to do but haven't gave enough availability

        #ABOUT WORKERS - if more than zero - etat workers have not enough hours
        unfilledHours = [0] * len(self.workers)
        for i in range(len(self.requiredHours)):
             
            if self.workers[i].howManyhours() < self.workers[i].etat:
                unfilledHours[i] = self.workers[i].etat - self.workers[i].howManyhours()
        
        needRotation = False

        

        #if places have all shifts occupied
        for place in self.places:
            if place.allShiftsOccupied() == False:

                needRotation = True
                break
        
        if needRotation == True:
            self.rotations()


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


    #move shifts because at first round we weren't able to fill all shifts
    def rotations(self):
        emptyShifts = []
       
        for place in self.places:
            
            for shift in place.schedule:
                if shift.worker == None:
                    emptyShifts.append(shift)


        while len(emptyShifts) != 0:

            #even if we don't find substitution we delete it from list
            theShift = emptyShifts.pop(0)

            #substitude - guywho we want to move to new shift location
            for substitude in self.whoCanWorkToday(theShift):

                #shift - zmiany, ktore musimy zastapic, aby przeniesienie pracownika mialo sens
                substutionGuys = [None] * len(substitude.list)
                allSubstitutions = True

                for i in range(len(substitude.list)):
                    #for collision shifts we look for new workers
                    #luckly those would until now couldn't work

                    newGuy = self.findSubstitution(substitude.list[i])

                    if( isinstance (newGuy, Worker)):
                        #we have substitution
                        #but be don't ably changes until we will have found all substitutions
                        substutionGuys[i] = newGuy
                    else:
                        allSubstitutions = False
                        #we can't find all substitutions for this change - abort changes
                        break

                           
                
                if allSubstitutions == True:
                    theShift.worker = substitude.worker

                    #we apply changes
                    for i in range(len(substitude.list)):
                        substitude.list[i].worker = substutionGuys[i]


                    #this rotation was successful
                    #now we need to save this rotations]
                    #so we want to it other way around!!!!!!!!!!!!!
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
                    










