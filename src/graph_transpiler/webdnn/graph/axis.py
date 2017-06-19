from enum import Enum, auto


# FIXME: DOCS
class Axis(Enum):
    N = auto()  # Batch size
    C = auto()  # Channel
    H = auto()  # Height
    W = auto()  # Width
    T = auto()  # Time
