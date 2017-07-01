from enum import Enum, auto


class Axis(Enum):
    """
    This class represents semantics of each dimension of variables.

    - :code:`Axis.N`

        number of samples (batch size), number of output channels in linear connection and convolution (number of filters).

    - :code:`Axis.C`

        number of features

    - :code:`Axis.H`

        height of image

    - :code:`Axis.W`

        width of image

    - :code:`Axis.T`

        length of series
    """
    N = auto()
    C = auto()
    H = auto()
    W = auto()
    T = auto()
