from enum import Enum, auto


class Axis(Enum):
    """
    Enum class for representing semantics of each dimension of variables.
    """
    N = auto()  #: Number of samples (batch size), number of output channels in linear connection and convolution (number of filters).
    C = auto()  #: Number of features
    H = auto()  #: Height of image
    W = auto()  #: Width of image
    T = auto()  #: Length of series
