from typing import Generic, TypeVar, List, Iterable, Tuple

_i = 0


def _unique():
    global _i
    _i += 1
    return f"__UNIQUE_{_i}__"


class Axis:
    """
    Enum class for representing semantics of each dimension of variables.
    """
    N = None  # type: "Axis"
    C = None  # type: "Axis"
    H = None  # type: "Axis"
    W = None  # type: "Axis"
    T = None  # type: "Axis"

    def __init__(self, name):
        if name is None:
            name = _unique()
        self._name = name

    @property
    def name(self):
        return self._name

    def __str__(self):
        return f"<Axis.{self.name}>"

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        # noinspection PyBroadException
        try:
            return other.name == self.name

        except Exception:
            return False

    __hash__ = None


T = TypeVar('T')


class AxisKeyDict(Generic[T]):
    def __init__(self, keys: Iterable[Axis] = None, vals: Iterable[T] = None):
        self._keys = list(keys if keys else [])  # type: List[Axis]
        self._vals = list(vals if vals else [])  # type: List[T]

    def __contains__(self, item: Axis) -> bool:
        return item in self._keys

    def __getitem__(self, item: Axis) -> T:
        index = self._keys.index(item)
        return self._vals[index]

    def __setitem__(self, key: Axis, value: T):
        if key in self:
            index = self._keys.index(key)
            self._vals[index] = value

        else:
            self._keys.append(key)
            self._vals.append(value)

    def __delitem__(self, key: Axis):
        index = self._keys.index(key)
        self._keys.pop(index)
        self._vals.pop(index)

    def __len__(self) -> int:
        return len(self._keys)

    def __iter__(self) -> Iterable[Axis]:
        return self.keys()

    def get(self, k: Axis, default: T) -> T:
        return self[k] if k in self else default

    def keys(self) -> Iterable[Axis]:
        return self._keys.__iter__()

    def values(self) -> Iterable[T]:
        return self._vals.__iter__()

    def items(self) -> Iterable[Tuple[Axis, T]]:
        return zip(self.keys(), self.values())


Axis.N = Axis("N")  #: Number of samples (batch size), number of output channels in linear connection and convolution (number of filters).
Axis.C = Axis("C")  #: Number of features
Axis.H = Axis("H")  #: Height of image
Axis.W = Axis("W")  #: Width of image
Axis.T = Axis("T")  #: Length of series
