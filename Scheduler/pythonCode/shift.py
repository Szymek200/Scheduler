from datetime import datetime, time, timedelta


class Shift:

    #many times can be used
    #datetime - specific date
    #or just time 
    def __init__(self, begin, end):
        self.begin = begin
        self.end = end
        
        #available places he wants to work

    def duration(self):
        return self.end - self.begin
    
    def __eq__(self, other):

        if self.begin == other.end and self.end == other.end:
            return True
        
        return False
    
    #shifts are equal or an argument fit inside hours of this shift
    def contains(self, shift):

        if isinstance(shift, Shift):

            if self.begin <= shift.begin and self.end >= shift.end:
                return True
            
        return False
    
    


        
#place shouldn't be set but just one particular object
class ShiftPlace(Shift):
     def __init__(self, begin, end, places, worker):
        super().__init__(begin, end)

        from worker import Worker
        #available places he wants to work
        if isinstance(places, set):
            self.places = places
            if isinstance(worker, Worker):
                self.worker = worker
        

     def __eq__(self, other):

        if self.begin == other.end and self.end == other.end:
            
            if self.places == other.places:
                return True
        
        return False
    
    #shifts are equal or an argument fit inside hours of this shift
     def contains(self, shift):

        if isinstance(shift, ShiftPlace):

            if self.begin <= shift.begin and self.end >= shift.end:

                #set intersection
                if self.places & shift.places:
                    return True 
        return False

    #equal everything except worker
     def sameShift(self, shift):
          if isinstance(shift, ShiftPlace):

            if self.begin == shift.begin and self.end == shift.end:

                #set intersection
                if self.places == shift.places:
                    return True 
            return False
        


