class Axis:
    """
    Enum class for representing semantics of each dimension of variables.
    """

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"<Axis.{self.name}>"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return isinstance(other, Axis) and self.name.__hash__() == other.name.__hash__()

    def __hash__(self):
        return self.name.__hash__()


N = Axis("N")  #: Number of samples (batch size), number of output channels in linear connection and convolution (number of filters).
C = Axis("C")  #: Number of features
H = Axis("H")  #: Height of image
W = Axis("W")  #: Width of image
T = Axis("T")  #: Length of series

Axis.N = N
Axis.C = C
Axis.H = H
Axis.W = W
Axis.T = T
