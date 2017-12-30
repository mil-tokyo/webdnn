class Attribute:
    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return self.__str__()
