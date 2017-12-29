import itertools
from enum import auto, Enum
from typing import Union, Optional, List, Sequence, Set, Tuple, Generic, TypeVar

import numpy as np

from webdnn.util import json
from webdnn.util.misc import mul


class PlaceholderOperator(Enum):
    Add = auto()  # v1 + v2
    Mul = auto()  # v1 * v2
    Mod = auto()  # v1 % v2
    EQ = auto()  # v1
    FloorDiv = auto()  # v1 // v2


T = TypeVar("T")
U = TypeVar("U")


class MutableCombinator(Generic[T]):
    """
    Iterator for combination. This iterator is mutable (items can be removed/appended anytime)

    Examples::

        a = [1, 2, 3, 4]
        comb = MutableCombinator(a, 2)

        for i, j in comb:
            print(i, j)
            if i == 2:
                comb.remove(i)

        >>> (1, 2),
            (1, 3),
            (1, 4),
            (2, 3), # Here, item "2" is removed and so combination "(2, 4)" does not appeared.
            (3, 4)

        print(comb.sequence)
        >>> (1, 3, 4)

    Arguments::
        sequence (Sequence) : item sequence
        r (int, optional) : length of each combination. Default is 2.
    """

    def __init__(self, sequence: Sequence[T], r: int = 2):
        self._sequence = list(sequence)  # type: List[T]
        self._combination = list(itertools.combinations(range(len(sequence)), r))  # type: List[Tuple[int, ...]]
        self._removed_indices = set()  # type: Set[int]
        self._r = r  # type: int

    def __iter__(self):
        return self

    def __next__(self, *args, **kwargs):
        while True:
            if len(self._combination) == 0:
                raise StopIteration

            ret = self._combination.pop(0)
            if all(i not in self._removed_indices for i in ret):
                break

        return tuple(self._sequence[i] for i in ret)

    def remove(self, x):
        i = -1
        while True:
            i = self._sequence.index(x, i + 1)
            if i not in self._removed_indices:
                break

        self._removed_indices.add(i)

    def append(self, x):
        i = len(self._sequence)
        self._sequence.append(x)
        self._combination += [(i,) + others for others in itertools.combinations(range(i), self._r - 1)]

    @property
    def sequence(self) -> Tuple[T, ...]:
        return tuple(v for i, v in enumerate(self._sequence) if i not in self._removed_indices)


class MutableProduct(Generic[T, U]):
    """
    Iterator for product of 2 sequences. This iterator is mutable (items can be removed/appended anytime)

    Examples::

        a = [1, 2, 3, 4]
        b = [5, 6, 7]
        prod = MutableProduct(a, b)

        for i, j in prod:
            print(i, j)
            prod.remove(0, i)

        >>> (1, 5), # Here, item "1" is removed and so pair "(1, 6)" and "(1, 7) do not appeared.
            (2, 5),
            (3, 5),
            (4, 5)

        print(prod.sequences)
        >>> ((), (5, 6, 7))

    Arguments::
        sequence1 (Sequence) : first sequence
        sequence2 (Sequence) : second sequence
    """

    def __init__(self, sequence1: Sequence[T], sequence2: Sequence[U]):
        self._sequences = (list(sequence1), list(sequence2))  # type: Tuple[List[T], List[U]]
        self._prod = list(itertools.product(range(len(sequence1)), range(len(sequence2))))  # type: List[Tuple[int, int]]
        self._removed_indices = (set(), set())  # type: Tuple[Set[int],Set[int]]

    def __iter__(self):
        return self

    def __next__(self) -> Tuple[T, U]:
        while True:
            if len(self._prod) == 0:
                raise StopIteration

            ret = self._prod.pop(0)
            if ret[0] not in self._removed_indices[0] and ret[1] not in self._removed_indices[1]:
                break

        return self._sequences[0][ret[0]], self._sequences[1][ret[1]]

    def remove(self, seq_index, x):
        i = -1
        while True:
            i = self._sequences[seq_index].index(x, i + 1)
            if i not in self._removed_indices[seq_index]:
                break

        self._removed_indices[seq_index].add(i)

    def append(self, seq_index, x):
        i = len(self._sequences[seq_index])
        self._sequences[seq_index].append(x)
        if seq_index == 0:
            self._prod += [(i, j) for j in range(len(self._sequences[1]))]
        else:
            self._prod += [(j, i) for j in range(len(self._sequences[0]))]

    @property
    def sequences(self) -> Tuple[Tuple[T, ...], Tuple[U, ...]]:
        return tuple(v for i, v in enumerate(self._sequences[0]) if i not in self._removed_indices[0]), \
               tuple(v for i, v in enumerate(self._sequences[1]) if i not in self._removed_indices[1])


class Dependency:
    operator: PlaceholderOperator
    operands: List[Union[int, "Placeholder"]]

    @staticmethod
    def check_deep_equal(d1: "Dependency", d2: "Dependency") -> bool:
        if d1.operator != d2.operator:
            return False

        if d1.operator == PlaceholderOperator.Mul or d1.operator == PlaceholderOperator.Add:
            operands1 = sorted(d1.operands, key=lambda op: str(op))
            operands2 = sorted(d2.operands, key=lambda op: str(op))
            if len(operands1) != len(operands2):
                return False

            return all([Placeholder.check_deep_equal(p1, p2) for p1, p2 in zip(operands1, operands2)])

        elif d1.operator == PlaceholderOperator.Mod or d1.operator == PlaceholderOperator.FloorDiv:
            is_d1_same = Placeholder.check_deep_equal(d1.operands[0], d2.operands[0])
            is_d2_same = Placeholder.check_deep_equal(d1.operands[1], d2.operands[1])
            return is_d1_same and is_d2_same

    def __init__(self, operator: PlaceholderOperator, operands: Sequence[Union[int, "Placeholder"]]):
        if operator == PlaceholderOperator.Mul or operator == PlaceholderOperator.Add:
            operands = list(sorted(operands, key=lambda op: str(op)))

        self.operator = operator
        self.operands = operands

    @property
    def is_resolved(self) -> bool:
        """
        If true, all dependent placeholders are resolved
        """
        if any((isinstance(operand, Placeholder) and not Placeholder.check_resolved(operand)) for operand in self.operands):
            return False

        return True

    @property
    def value(self) -> Union[int, "Placeholder"]:
        if not self.is_resolved:
            raise ValueError("Dependency is not resolved")

        if self.operator == PlaceholderOperator.Add:
            r = 0
            for v in self.operands:
                r += Placeholder.force_int(v)
            return r

        elif self.operator == PlaceholderOperator.Mul:
            r = 1
            for v in self.operands:
                r *= Placeholder.force_int(v)
            return r

        elif self.operator == PlaceholderOperator.Mod:
            return Placeholder.force_int(self.operands[0]) % Placeholder.force_int(self.operands[1])

        elif self.operator == PlaceholderOperator.FloorDiv:
            return Placeholder.force_int(self.operands[0]) // Placeholder.force_int(self.operands[1])

        else:
            raise NotImplementedError(f"Unsupported placeholder operation: {self.operator}")

    def __repr__(self):
        if self.operator == PlaceholderOperator.Add:
            return " + ".join(map(lambda x: x.__repr__(), self.operands))

        s = []
        for v in self.operands:
            if Placeholder.check_resolved(v):
                s.append(str(v))

            elif v.dependency and len(v.dependency.operands) > 1:
                s.append("(" + v.__repr__() + ")")

            else:
                s.append(v.__repr__())

        if self.operator == PlaceholderOperator.Mul:
            return " * ".join(s)

        elif self.operator == PlaceholderOperator.Mod:
            return " % ".join(s)

        elif self.operator == PlaceholderOperator.FloorDiv:
            return " // ".join(s)

        raise NotImplementedError(f"Unsupported placeholder operation: {self.operator}")

    def dump(self):
        if self.operator == PlaceholderOperator.Add:
            return "(" + self.operands[0].dump() + " + " + self.operands[1].dump() + ")"

        elif self.operator == PlaceholderOperator.Mul:
            return self.operands[0].dump() + " * " + self.operands[1].dump()

        elif self.operator == PlaceholderOperator.Mod:
            return self.operands[0].dump() + " % " + self.operands[1].dump()

        elif self.operator == PlaceholderOperator.FloorDiv:
            return self.operands[0].dump() + " // " + self.operands[1].dump()

        else:
            raise NotImplementedError(f"Unsupported placeholder operation: {self.operator}")

    def generate_js_function(self):
        if self.operator == PlaceholderOperator.Add:
            return " + ".join(map(lambda x: x.generate_js_function(flag_semicolon=False), self.operands))

        s = []
        for v in self.operands:
            if Placeholder.check_resolved(v):
                s.append(str(v))

            else:
                if v.dependency and len(v.dependency.operands) > 1:
                    s.append("(" + v.generate_js_function(flag_semicolon=False) + ")")
                else:
                    s.append(v.generate_js_function(flag_semicolon=False))

        if self.operator == PlaceholderOperator.Mul:
            return " * ".join(s)

        elif self.operator == PlaceholderOperator.Mod:
            return " % ".join(s)

        elif self.operator == PlaceholderOperator.FloorDiv:
            assert len(s) == 2
            return f"Math.floor({s[0]} / {s[1]})"

        raise NotImplementedError(f"Unsupported placeholder operation: {self.operator}")


_id = 0


class Placeholder(json.SerializableMixin):
    """Placeholder(value=None, label=None)

    Placeholder represents values which are unknown at compile time and determined at runtime, like batch size, length of
    time series, etc.

    Placeholder supports only integer value.

    Placeholder is embedded in graph descriptor and resolved at runtime like follows:

    .. code-block:: javascript

        runner = await WebDNN.load('./my_model');
        await runner.setPlaceholderValue({
            'N': 8
        });

    Also Placeholder can be resolved by setting concrete value at compile time.

        >>> x = Placeholder(label="x")
        >>> print(x)
        <x>
        >>> x.value = 3
        >>> print(x)
        3
        >>> print(type(x))
        <class 'webdnn.graph.placeholder.Placeholder'>

    Placeholder supports follow basic operations.

    - add(:code:`+`), sub(:code:`-`), mul(:code:`*`), mod(:code:`%`), floor-div(:code:`//`).

        >>> x = Placeholder(label="x")
        >>> y = x * 2 + 3
        >>> print(y)
        <x> * 2 + 3

        >>> x = Placeholder(label="x")
        >>> y = x % 4 // 5
        >>> print(y)
        (<x> % 4) // 5

        If possible, equation are simplified

        >>> x = Placeholder(label="x")
        >>> y = x * 6 + x * 7
        >>> print(y)
        <x> * 13

    - eq(:code:`==`), ne(:code:`!=`)

        If both placeholders are resolved, they are compared based on concrete values.

        >>> p = Placeholder(value=3)
        >>> x = p * 2
        >>> y = p + p
        >>> print(x == y == 6)
        True

        If either placeholder is not resolved, they are compared symbolically.

        >>> p = Placeholder(label="p")
        >>> x = p * 2
        >>> y = p * 3
        >>> print(x == y)
        False
        >>> p.value = 0
        >>> print(x == y)
        True

    - gt(:code:`>`), lt(:code:`<`), ge(:code:`>=`), le(:code:`<=`)

        Supported only when both placeholders are resolved. Otherwise, an error is raised.

        >>> p = Placeholder(label="p")
        >>> x = p * 2
        >>> y = p * 3
        >>> print(x < y)
        ValueError: First operand is unresolved placeholder. It can't be compared.
        >>> p.value = 3
        >>> print(x < y)
        True

    Attributes:
        label (str): the label.
    """
    _value = None  # type: Optional[int]
    label = None  # type: Optional[str]
    dependency = None  # type: Optional[Dependency]

    @staticmethod
    def to_int(x: Union[int, "Placeholder"]):
        """to_int(x)

        Convert the placeholder into concrete integer value.
        Args:
            x: the placeholder

        Returns:
            (int or Placeholder): If `x` is resolved, an integer is returned. Otherwise, `x` itself is returned.
        """
        return int(x) if not isinstance(x, Placeholder) else int(x.value) if Placeholder.check_resolved(x) else x

    @staticmethod
    def force_int(x: Union[int, "Placeholder"]):
        """force_int(x)

        Convert the placeholder into concrete integer value. If `x` is not resolved, an error is raised.
        Args:
            x: the placeholder

        Returns:
            (int): an integer
        """
        if not isinstance(x, Placeholder):
            return int(x)

        elif Placeholder.check_resolved(x):
            return x.value

        raise ValueError(f"{x} is not resolved.")

    @staticmethod
    def check_resolved(x: Union[int, "Placeholder"]):
        """check_resolved(x)

        Check whether specified placeholder is resolved or not.
        Args:
            x: the placeholder

        Returns:
            (bool): If `True`, the placeholder is resolved. Otherwise, it's not resolved.
        """
        if not isinstance(x, Placeholder):
            return True

        if x._value is not None:
            return True

        if x.dependency:
            return x.dependency.is_resolved

        return False

    @staticmethod
    def check_deep_equal(p1: Union[int, "Placeholder"], p2: Union[int, "Placeholder"]) -> bool:
        if str(p1) == str(p2):
            return True

        elif Placeholder.check_resolved(p1) and Placeholder.check_resolved(p2):
            return Placeholder.force_int(p1) == Placeholder.force_int(p2)

        elif Placeholder.check_resolved(p1) or Placeholder.check_resolved(p2):
            return False

        elif p1.dependency is not None and p2.dependency is not None:
            return Dependency.check_deep_equal(p1.dependency, p2.dependency)

        else:
            return False

    def __new__(cls, dependency: Optional[Dependency] = None, value: Union[int, "Placeholder"] = None, label: str = None):
        if isinstance(value, Placeholder):
            return value

        return super().__new__(cls)

    def __init__(self, dependency: Optional[Dependency] = None, value: Union[int, "Placeholder"] = None, label: Optional[str] = None):
        global _id

        if self is value:
            return

        self.dependency = dependency
        if label is None:
            self.label = f"placeholder_[{_id}]"
            _id += 1
        else:
            self.label = label

        if value is not None:
            self.value = value

    @property
    def value(self) -> Union[int, "Placeholder"]:
        """value

        The placeholder's value. If it's not resolved, the placeholder itself is returned.

        If the placeholder is already resolved, new value cannot be set, and it causes an error.
        """
        if Placeholder.check_resolved(self):
            if self.dependency:
                if self._value is None:
                    self._value = self.dependency.value

            return self._value

        else:
            return self

    @value.setter
    def value(self, new_v: int):
        if Placeholder.check_resolved(self):
            raise ValueError(f"{self} is already resolved")

        elif isinstance(new_v, int) or isinstance(new_v, np.int32) or isinstance(new_v, np.int64):
            # noinspection PyTypeChecker
            self._value = int(new_v)

        else:
            raise TypeError(f"Placeholder#value must be a int, not '{type(new_v)}'")

    def unify(self, other: Union[int, "Placeholder"]):
        if Placeholder.check_resolved(self) and Placeholder.check_resolved(other):
            assert self == other, f"""
Unification failed: self != other
  (self) = {self}
  (other) = {other}"""

        elif Placeholder.check_resolved(self) and not Placeholder.check_resolved(other):
            other.value = self.value

        elif not Placeholder.check_resolved(self) and Placeholder.check_resolved(self):
            self.value = other.value

        else:
            #  FIXME
            pass

    @property
    def _operator(self):
        if Placeholder.check_resolved(self):
            return None

        elif self.dependency is None:
            return None

        else:
            return self.dependency.operator

    @property
    def _operands(self):
        if Placeholder.check_resolved(self):
            return [self.value]

        elif self.dependency is None:
            return [self]

        else:
            return list(self.dependency.operands)

    def __neg__(self) -> Union[int, "Placeholder"]:
        return -1 * self

    def __add__(self, other: Union[int, "Placeholder"]) -> Union[int, "Placeholder"]:
        v1, v2 = self, Placeholder(value=other)

        if v2 == 0:
            return v1

        if v1 == 0:
            return v2

        if Placeholder.check_resolved(v1) and Placeholder.check_resolved(v2):
            return v1.value + v2.value

        # flatten: (v1_0 + v1_1) + (v2_0 + v2_1) -> (v1_0 + v1_1 + v1_2 + v1_3)
        terms = []  # type: List[Union[Placeholder, int]]
        terms += list(v1._operands) if v1._operator == PlaceholderOperator.Add else [v1]
        terms += list(v2._operands) if v2._operator == PlaceholderOperator.Add else [v2]
        len_terms = len(terms)

        # sum resolved values
        resolved_value = 0
        for vv in list(terms):
            if Placeholder.check_resolved(vv):
                terms.remove(vv)
                resolved_value += vv

        if resolved_value != 0:
            terms.append(resolved_value)

        # factorize: (v1 * v3) + (v2 * v3) -> (v1+v2) * v3
        comb = MutableCombinator(terms)
        for vv1, vv2 in comb:
            if not isinstance(vv1, Placeholder) or not isinstance(vv2, Placeholder):
                continue

            if (vv1._operator is None or vv1._operator == PlaceholderOperator.Mul) and \
                (vv2._operator is None or vv2._operator == PlaceholderOperator.Mul):
                operands_vv1 = list(vv1._operands)
                operands_vv2 = list(vv2._operands)
                common_term = list()

                for vvv in list(operands_vv1):
                    if vvv in operands_vv2:
                        operands_vv1.remove(vvv)
                        operands_vv2.remove(vvv)
                        common_term.append(vvv)

                if len(common_term) >= 1:
                    # If either vv1 or vv2 is not resolved, this rule conflicts with expanding in __mul__
                    if Placeholder.check_resolved(mul(operands_vv1)) and Placeholder.check_resolved(mul(operands_vv2)):
                        comb.remove(vv1)
                        comb.remove(vv2)
                        comb.append(mul(common_term) * (mul(operands_vv1) + mul(operands_vv2)))

        terms = comb.sequence
        if len(terms) < len_terms:
            return sum(terms)

        return Placeholder(Dependency(PlaceholderOperator.Add, terms))

    def __radd__(self, other: Union[int, "Placeholder"]) -> Union[int, "Placeholder"]:
        return Placeholder(value=other) + self

    def __sub__(self, other: Union[int, "Placeholder"]) -> Union[int, "Placeholder"]:
        if other == 0:
            return self

        return self + (-1 * other)

    def __rsub__(self, other: Union[int, "Placeholder"]) -> Union[int, "Placeholder"]:
        return Placeholder(value=other) - self

    def __mul__(self, other: Union[int, "Placeholder"]) -> Union[int, "Placeholder"]:
        v1, v2 = self, Placeholder(value=other)

        if v1 == 0 or v2 == 0:
            return 0

        if v1 == 1:
            return v2

        if v2 == 1:
            return v1

        if Placeholder.check_resolved(v1) and Placeholder.check_resolved(v2):
            return v1.value * v2.value

        # flatten: (v1_0 * v1_1) * (v2_0 * v2_1) -> (v1_0 * v1_1 * v1_2 * v1_3)
        terms = []
        terms += list(v1._operands) if v1._operator == PlaceholderOperator.Mul else [v1]
        terms += list(v2._operands) if v2._operator == PlaceholderOperator.Mul else [v2]

        # sum resolved values
        resolved_value = 1
        for vv in list(terms):
            if Placeholder.check_resolved(vv):
                terms.remove(vv)
                resolved_value *= vv

        if resolved_value != 1:
            terms.append(resolved_value)

        for vv in terms:
            if isinstance(vv, Placeholder) and vv._operator == PlaceholderOperator.Add:
                # expanding: (v1_0 + v1_1 + ...) * v2 = (v1_0 * v2) + (v1_1 * v2) + ...
                terms.remove(vv)
                return sum(mul(terms) * v for v in vv._operands)

        return Placeholder(Dependency(PlaceholderOperator.Mul, terms))

    def __rmul__(self, other: Union[int, "Placeholder"]) -> Union[int, "Placeholder"]:
        return Placeholder(value=other) * self

    def __floordiv__(self, other: Union[int, "Placeholder"]) -> Union[int, "Placeholder"]:
        v1, v2 = self, Placeholder(value=other)

        if v2 == 1:
            return v1

        if v1 == 0:
            return 0

        if v1 == v2:
            return 1

        if Placeholder.check_resolved(v1) and Placeholder.check_resolved(v2):
            return v1.value // v2.value

        if v1._operator == PlaceholderOperator.Add:
            operands_v1 = list(v1._operands)
            divided = []
            for vv1 in list(operands_v1):
                if vv1 % v2 != 0:
                    continue

                operands_v1.remove(vv1)
                divided.append(vv1 // v2)

            if len(divided) > 0:
                return sum(divided + [sum(operands_v1) // v2])

        if v1._operator == PlaceholderOperator.FloorDiv:
            v1_1, v1_2 = v1._operands
            if Placeholder.check_resolved(v1_2) and Placeholder.check_resolved(v2):
                return v1_1 // (v1_2 * v2)

        if (v1._operator is None or v1._operator == PlaceholderOperator.Mul) and \
            (v2._operator is None or v2._operator == PlaceholderOperator.Mul):
            operands_v1 = list(v1._operands)
            operands_v2 = list(v2._operands)

            prod = MutableProduct(operands_v1, operands_v2)
            for vv1, vv2 in prod:
                if vv1 % vv2 != 0:
                    continue

                prod.remove(0, vv1)
                prod.remove(1, vv2)
                prod.append(0, vv1 // vv2)

            new_operands_v1, new_operands_v2 = prod.sequences
            if len(new_operands_v2) == 0:
                return mul(new_operands_v1)

            else:
                if len(new_operands_v1) == 0:
                    # 1 // v2 == 0
                    return 0

                else:
                    v1 = mul(new_operands_v1)
                    v2 = mul(new_operands_v2)
                    return Placeholder(Dependency(PlaceholderOperator.FloorDiv, [v1, v2]))

        return Placeholder(Dependency(PlaceholderOperator.FloorDiv, [v1, v2]))

    def __rfloordiv__(self, other: Union[int, "Placeholder"]) -> Union[int, "Placeholder"]:
        return Placeholder(value=other) // self

    def __mod__(self, other: Union[int, "Placeholder"]) -> Union[int, "Placeholder"]:
        v1, v2 = self, Placeholder(value=other)

        if v1 == v2:
            return 0

        if v2 == 1:
            return 0

        if Placeholder.check_resolved(v1) and Placeholder.check_resolved(v2):
            return v1.value % v2.value

        if (v1._operator is None or v1._operator == PlaceholderOperator.Mul) and (
            v2._operator is None or v2._operator == PlaceholderOperator.Mul):
            # v = ... + (common_term * other_term1) % (common_term * other_term2) + ...
            #   = ... + (other_term1 % other_term2) * common_term + ...
            prod = MutableProduct(v1._operands, v2._operands)
            common_term = []
            flag_updated = False
            for vv1, vv2 in prod:
                if (Placeholder.check_resolved(vv1) and Placeholder.check_resolved(vv2) and vv1 % vv2 == 0) or vv1 == vv2:
                    flag_updated = True
                    prod.remove(0, vv1)
                    prod.remove(1, vv2)
                    prod.append(0, vv1 // vv2)
                    common_term.append(vv2)

            if flag_updated:
                new_operands_v1, new_operands_v2 = prod.sequences
                return (mul(new_operands_v1) % mul(new_operands_v2)) * mul(common_term)

        return Placeholder(Dependency(PlaceholderOperator.Mod, [v1, v2]))

    def __rmod__(self, other: Union[int, "Placeholder"]) -> Union[int, "Placeholder"]:
        return Placeholder(value=other) % self

    def __int__(self):
        return Placeholder.force_int(self)

    def __eq__(self, other: Union[int, "Placeholder"]) -> bool:
        return Placeholder.check_deep_equal(self, other)

    def __ne__(self, other: Union[int, "Placeholder"]) -> bool:
        return not Placeholder.check_deep_equal(self, other)

    def __gt__(self, other: Union[int, "Placeholder"]) -> bool:
        if not Placeholder.check_resolved(self):
            raise ValueError("First operand is unresolved placeholder. It can't be compared.")

        if not Placeholder.check_resolved(other):
            raise ValueError("Second operand is unresolved placeholder. It can't be compared.")

        return self.value > Placeholder.force_int(other)

    def __lt__(self, other: Union[int, "Placeholder"]) -> bool:
        if not Placeholder.check_resolved(self):
            raise ValueError("First operand is unresolved placeholder. It can't be compared.")

        if not Placeholder.check_resolved(other):
            raise ValueError("Second operand is unresolved placeholder. It can't be compared.")

        return self.value < Placeholder.force_int(other.value)

    def __ge__(self, other: Union[int, "Placeholder"]) -> bool:
        if not Placeholder.check_resolved(self):
            raise ValueError("First operand is unresolved placeholder. It can't be compared.")

        if not Placeholder.check_resolved(other):
            raise ValueError("Second operand is unresolved placeholder. It can't be compared.")

        return self.value >= Placeholder.force_int(other)

    def __le__(self, other: Union[int, "Placeholder"]) -> bool:
        if not Placeholder.check_resolved(self):
            raise ValueError("First operand is unresolved placeholder. It can't be compared.")

        if not Placeholder.check_resolved(other):
            raise ValueError("Second operand is unresolved placeholder. It can't be compared.")

        return self.value <= Placeholder.force_int(other)

    def __repr__(self):
        if Placeholder.check_resolved(self):
            return str(self.value)

        else:
            if self.dependency:
                return self.dependency.__repr__()

            else:
                return f"<{self.label}>" if self.label else f"<{self.__class__.__name__} at {hex(id(self))}>"

    def __hash__(self):
        return id(self)

    def dump(self):
        if self.dependency:
            return self.dependency.dump()

        elif self._value is not None:
            return str(self._value)

        else:
            return f"<{self.label}>" if self.label else f"<{self.__class__.__name__} at {hex(id(self))}>"

    def _to_serializable_(self):
        if Placeholder.check_resolved(self):
            return self.value

        else:
            return {
                "eval": self.generate_js_function()
            }

    def get_depend_placeholders(self):
        """get_depend_placeholders

        List up all dependent placeholders

        Returns:
            (list of Placeholder): list of all dependent placeholders
        """
        if Placeholder.check_resolved(self):
            return set()

        if self.dependency:
            res = set()
            for v in self.dependency.operands:
                if not Placeholder.check_resolved(v):
                    res.update(v.get_depend_placeholders())

            return res

        else:
            return {self}

    def generate_js_function(self, flag_semicolon=True):
        """generate_js_function

        Generate javascript code to resolve this placeholder's value at runtime.

        Args:
            flag_semicolon(bool): If True, semicolon is appended into generated code.

        Returns:
            (str): generated code
        """
        if Placeholder.check_resolved(self):
            return f"{self.value}" + (";" if flag_semicolon else "")

        else:
            if self.dependency:
                return self.dependency.generate_js_function()

            else:
                return f"placeholders['{self.label}']" + (";" if flag_semicolon else "")
