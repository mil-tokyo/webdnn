from typing import Generic, Iterable, Tuple, Union, TypeVar, List, Dict

_internal2global = {}  # type: Dict[int, int]
_global2internal = {}  # type: Dict[int, List[int]]
_axis_name_dict = {}  # type: Dict[int, str]

_uuid_counter = 0


class UnificationFailedError(Exception):
    pass


class Axis:
    """
    Enum class for representing semantics of each dimension of variables.
    """
    N = None  # type: "Axis"
    C = None  # type: "Axis"
    H = None  # type: "Axis"
    W = None  # type: "Axis"
    T = None  # type: "Axis"
    KH = None  # type: "Axis"
    KW = None  # type: "Axis"

    def __init__(self, name=None):
        global _uuid_counter
        internal_id = _uuid_counter
        _uuid_counter += 1
        global_id = internal_id

        _internal2global[internal_id] = global_id
        _global2internal[global_id] = [internal_id]
        _axis_name_dict[global_id] = name

        self._internal_id = internal_id

    def __str__(self):
        return f"<Axis {self.name}>"

    def __repr__(self):
        return self.__str__()

    @property
    def id(self) -> int:
        return _internal2global[self._internal_id]

    @property
    def name(self) -> str:
        name = _axis_name_dict[self.id]
        return f"?{self.id}" if name is None else name

    @property
    def resolved(self) -> str:
        return _axis_name_dict[self.id] is not None

    def unify(self, other: "Axis"):
        if self.id == other.id:
            return

        if self.resolved and other.resolved:
            if self.name != other.name:
                raise UnificationFailedError(f"""
Unification failed: Both "self" and "other" have been resolved with different values.
    (self.name) = {self.name}
    (other.name) = {other.name}""")

        other_id = other.id
        _axis_name_dict[self.id] = self.name if self.resolved else _axis_name_dict[other.id]
        p1s = _global2internal[self.id]
        p2s = _global2internal[other_id]
        del _global2internal[other_id]
        del _axis_name_dict[other_id]

        for p2 in p2s:
            p1s.append(p2)
            _internal2global[p2] = self.id

    def __eq__(self, other):
        if not isinstance(other, Axis):
            return False

        return self.id == other.id

    __hash__ = None


T = TypeVar('T')


class AxisKeyDict(Generic[T]):
    """
    Axis is not hashable, dictionary cannot use axis object as key. AxisKeyDict allow using axis as key.
    """

    def __init__(self, keys: Union[Iterable[Axis], "AxisKeyDict"] = None, vals: Iterable[T] = None):
        if isinstance(keys, AxisKeyDict):
            self._keys = list(keys.keys())
            self._vals = list(keys.values())

        else:
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

    def __str__(self) -> str:
        return "{" + ", ".join(a.name + ':' + str(v) for a, v in self.items()) + "}"

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
Axis.KH = Axis("KH")  #: Height of image
Axis.KW = Axis("KW")  #: Width of image
