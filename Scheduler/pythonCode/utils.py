from datetime import timedelta

def hoursSum(shiftList):
    hourSum = timedelta(0)
    for shift in shiftList:
        hourSum += shift.duration()
    return hourSum