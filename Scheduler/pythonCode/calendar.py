from datetime import datetime, time, timedelta

class Calendar:
    def __init__(month):
        
        self.destination = today.replace(month=month, day=1)
        
        #returns tuple - first day of the month - 0 
        #1 - number of days
        self.total_days = calendar.monthrange(self.destination.year, self.destination.month)[1]

        
        self.shiftList = []


def add_shift(self, shift_object):
        if isinstance(shift_object, Shift):
            self.shift_list.append(shift_object)
        #else:
            #throw exception

def add_shifts(self, shift_list):
        if isinstance(shift_list, list) and all(isinstance(item, Shift) for item in shift_list):
            for shift in shift_list:
                self.shift_list.append(shift)

def sortShifts(self):
     self.shift_list.sort(key=lambda x: x.begin.)
     