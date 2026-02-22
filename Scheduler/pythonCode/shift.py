from datetime import datetime, time, timedelta

class Shift:

    #many times can be used
    #datetime - specific date
    #or just time 
    def __init__(self, begin, end):
        self.begin = begin
        self.end = end

