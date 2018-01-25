import itertools
from typing import TypeVar, List, Dict, Generic, Sequence, Iterable, Tuple

_internal2global = {}  # type: Dict[int, int]
_global2internal = {}  # type: Dict[int, List[int]]
_axis_name_dict = {}  # type: Dict[int, str]

_uuid_counter = 0


def _uuid():
    global _uuid_counter
    _uuid_counter += 1
    return _uuid_counter


class Axis:
    """Axis(name=None)

    Class `Axis` represents the dimension of :class:`~webdnn.graph.variable.Variable`. Axis is container and the represented dimension
    would be changed.

    .. admonition:: example

        .. code:: py

            # a1 and a2 represent different dimensions
            a1 = Axis()
            a2 = Axis()

            v1 = Variable([3, 5], Order([a1, a2))
            >>> "<Variable shape=[3, 5] order=[?1, ?2]>"

            # unify a1 and a2 (= let them represent the same dimension)
            a1.unify(a2)

            v2 = Variable([3, 5], Order([a1, a2))
            >>> ValueError: "Axes are duplicated: [?1, ?1]"

    Args:
        name (str, optional) : axis name
    """

    def __init__(self, name=None):
        """
        Each `Axis` object has an unique internal id, which is not changed forever. Also each axis has another id called "global id", which
        would be changed and not unique over axes. Global id is used to identify two axes as same.
        """
        self._internal_id = _uuid()
        global_id = self._internal_id

        _internal2global[self._internal_id] = global_id
        _global2internal[global_id] = [self._internal_id]
        _axis_name_dict[global_id] = name

    def __str__(self):  # pragma: no cover
        return f"<Axis {self.name}>"

    def __repr__(self):  # pragma: no cover
        return self.__str__()

    @property
    def id(self) -> int:
        """axis's id, which is used to identify the which dimension the axis represents to"""
        return _internal2global[self._internal_id]

    @property
    def name(self) -> str:
        """axis's name"""
        name = _axis_name_dict[self.id]
        return f"?{self.id}" if name is None else name

    def unify(self, other: "Axis"):
        """
        Unify two axes object. It means that they represents to same dimension. To unify two axes, they must not have different names.

        Args:
            other (:class:`~webdnn.graph.axis.Axis`) : the axis object which will be unified with this axis object.
        """
        if self.id == other.id:
            # Already two axes are unified
            return

        # If both two axes have name, they must be same
        if (_axis_name_dict[self.id] is not None) and (_axis_name_dict[other.id] is not None) and (self.name != other.name):
            raise TypeError(f"""
Unification failed: "self" and "other" must have same name.
    (self.name) = {self.name}
    (other.name) = {other.name}""")

        # Unification

        # 1. Update "other"'s global id as same as "self"'s
        other_id = other.id
        _axis_name_dict[self.id] = self.name if (_axis_name_dict[self.id] is not None) else _axis_name_dict[other.id]

        # 2. For all axes which has same global id as "other", update their global id as same as "self"'s
        for internal_id in _global2internal[other_id]:
            _internal2global[internal_id] = self.id
            _global2internal[self.id].append(internal_id)

        del _global2internal[other_id]
        del _axis_name_dict[other_id]

    def __eq__(self, other):
        if not isinstance(other, Axis):
            return False

        return self.id == other.id

    __hash__ = None  # "Axis" is mutable container and hash value would be changed

    # Pre-declared axes
    N = None  # type: Axis
    C = None  # type: Axis
    H = None  # type: Axis
    W = None  # type: Axis
    T = None  # type: Axis
    KH = None  # type: Axis
    KW = None  # type: Axis


Axis.N = Axis("N")  # Number of samples (batch size), number of output channels in linear connection and convolution (number of filters).
Axis.C = Axis("C")  # Number of features
Axis.H = Axis("H")  # Height of image
Axis.W = Axis("W")  # Width of image
Axis.T = Axis("T")  # Length of series
Axis.KH = Axis("KH")  # Height of filter kernel
Axis.KW = Axis("KW")  # Width of filter kernel

T = TypeVar('T')


class AxisKeyDict(Generic[T]):
    """AxisKeyDict(*args)

    Dictionary-like object. Since :class:`~webdnn.graph.axis.Axis` is not hashable, dictionary cannot use axis object as key. AxisKeyDict
    allows using axis as key.

    You can instantiate `AxisKeyDict` by various way

    - If only `AxisKeyDict` instance is given, shallow-copied AxisKeyDict instance is created.
    - If only tuple of pairs of `Axis` and value is given, dictionary with specified keys and values is created.
    - If two sequences of same length are given, dictionary with specified key-value pairs is created
    - If nothing is given, empty dictionary is created.
    - Otherwise `ValueError` is raised.
    """

    def __init__(self, *args):
        if len(args) == 0:
            # nothing is given
            keys = []
            values = []

        elif len(args) == 1 and isinstance(args[0], AxisKeyDict):
            # other
            keys = list(args[0].keys())
            values = list(args[0].values())

        elif len(args) == 1 and isinstance(args[0], Sequence):
            # keyvals
            keys = [k for k, v in args[0]]
            values = [v for k, v in args[0]]

        elif len(args) == 2 and isinstance(args[0], Sequence) and isinstance(args[1], Sequence):
            # keys and values
            keys = list(args[0])
            values = list(args[1])
            if len(keys) != len(values):
                raise ValueError(f"""
[AxisKeyDict] Parameter "keys" and "values" must be same length:
    (keys) = {keys}
    (values) = {values}
    (len(keys)) = {len(keys)}
    (len(values)) = {len(values)}""")

            for a1, a2 in itertools.combinations(keys, 2):
                if a1 == a2:
                    raise ValueError(f"""
[AxisKeyDict] Axes are duplicated in parameter "keys":
    (keys) = {keys}
    (duplicated axis) = {a1}""")

        else:
            raise ValueError(f"""
[AxisKeyDict] Invalid parameters are given
    (args) = {args}""")

        self._keys = keys
        self._values = values

    def __contains__(self, item: Axis) -> bool:
        return item in self._keys

    def __getitem__(self, item: Axis) -> T:
        index = self._keys.index(item)
        return self._values[index]

    def __setitem__(self, key: Axis, value: T):
        if key in self:
            index = self._keys.index(key)
            self._values[index] = value

        else:
            self._keys.append(key)
            self._values.append(value)

    def __delitem__(self, key: Axis):
        index = self._keys.index(key)
        self._keys.pop(index)
        self._values.pop(index)

    def __len__(self) -> int:
        return len(self._keys)

    def __iter__(self) -> Iterable[Axis]:
        return self.keys()

    def __str__(self) -> str:  # pragma: no coverage
        return "{" + ", ".join(a.name + ':' + str(v) for a, v in self.items()) + "}"

    def __repr__(self) -> str:  # pragma: no coverage
        return self.__str__()

    def get(self, k: Axis, default: T) -> T:
        return self[k] if k in self else default

    def keys(self) -> Iterable[Axis]:
        return self._keys.__iter__()

    def values(self) -> Iterable[T]:
        return self._values.__iter__()

    def items(self) -> Iterable[Tuple[Axis, T]]:
        return zip(self.keys(), self.values())
