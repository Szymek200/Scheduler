class Worker:

    #class variable

    availableId = 1


    def __init__(self, name, surname, pesel, isFullTime):
        self.name = name
        self.surname = surname
        self.pesel = pesel

        self.id = self.availableId
        self.availableId += 1

        if(isFullTime == True):
            self.fullTime = 1

       


