class Place:

    #class variable

    availableId = 1


    def __init__(self, name, address):
        self.name = name
        self.address = address
        self.id = self.availableId

        self.availableId += 1
        

