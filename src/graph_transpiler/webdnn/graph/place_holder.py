from enum import auto, Enum
from typing import Union, Optional, Sequence

from webdnn.util.json import json


class PlaceHolderOperator(Enum):
    Add = auto()  # v1 + v2
    Sub = auto()  # v1 - v2
    Mul = auto()  # v1 * v2
    Mod = auto()  # v1 % v2
    FloorDiv = auto()  # v1 // v2


class Dependency:
    operator: PlaceHolderOperator
    operands: Sequence[Union[int, "PlaceHolder"]]

    def __init__(self, operator: PlaceHolderOperator, operands: Sequence[Union[int, "PlaceHolder"]]):
        self.operator = operator
        self.operands = operands

    @property
    def is_resolved(self) -> bool:
        """
        If true, all dependent placeholders are resolved
        """
        for operand in self.operands:
            if isinstance(operand, PlaceHolder) and not operand.is_resolved:
                return False

        return True

    @property
    def value(self) -> Union[int, "PlaceHolder"]:
        if not self.is_resolved:
            return PlaceHolder(self)

        if self.operator == PlaceHolderOperator.Add:
            return self.operands[0].value + self.operands[1].value

        elif self.operator == PlaceHolderOperator.Sub:
            return self.operands[0].value - self.operands[1].value

        elif self.operator == PlaceHolderOperator.Mul:
            return self.operands[0].value * self.operands[1].value

        elif self.operator == PlaceHolderOperator.Mod:
            return self.operands[0].value % self.operands[1].value

        elif self.operator == PlaceHolderOperator.FloorDiv:
            return self.operands[0].value // self.operands[1].value

        else:
            raise NotImplementedError(f"Unsupported placeholder operation: {self.operator}")

    def __repr__(self):
        if self.operator == PlaceHolderOperator.Add:
            return "(" + self.operands[0].__repr__() + " + " + self.operands[1].__repr__() + ")"

        elif self.operator == PlaceHolderOperator.Sub:
            return "(" + self.operands[0].__repr__() + " - " + self.operands[1].__repr__() + ")"

        elif self.operator == PlaceHolderOperator.Mul:
            return self.operands[0].__repr__() + " * " + self.operands[1].__repr__()

        elif self.operator == PlaceHolderOperator.Mod:
            return self.operands[0].__repr__() + " % " + self.operands[1].__repr__()

        elif self.operator == PlaceHolderOperator.FloorDiv:
            return self.operands[0].__repr__() + " // " + self.operands[1].__repr__()

        else:
            raise NotImplementedError(f"Unsupported placeholder operation: {self.operator}")

    def dump(self):
        if self.operator == PlaceHolderOperator.Add:
            return "(" + self.operands[0].dump() + " + " + self.operands[1].dump() + ")"

        elif self.operator == PlaceHolderOperator.Sub:
            return "(" + self.operands[0].dump() + " - " + self.operands[1].dump() + ")"

        elif self.operator == PlaceHolderOperator.Mul:
            return self.operands[0].dump() + " * " + self.operands[1].dump()

        elif self.operator == PlaceHolderOperator.Mod:
            return self.operands[0].dump() + " % " + self.operands[1].dump()

        elif self.operator == PlaceHolderOperator.FloorDiv:
            return self.operands[0].dump() + " // " + self.operands[1].dump()

        else:
            raise NotImplementedError(f"Unsupported placeholder operation: {self.operator}")


class PlaceHolder(json.SerializableMixin):
    _value: Optional[int] = None
    _cache_value = None
    dependency: Optional[Dependency] = None

    @staticmethod
    def to_int(x: Union[int, "PlaceHolder"]):
        if isinstance(x, int):
            return x

        if x.is_resolved:
            return x.value if x.is_resolved else x

    @staticmethod
    def force_int(x: Union[int, "PlaceHolder"]):
        if isinstance(x, int):
            return x

        if x.is_resolved:
            return x.value

        raise ValueError(f"{x} is not resolved.")

    def __new__(cls, dependency: Optional[Dependency] = None, value: Union[int, "PlaceHolder"] = None):
        if isinstance(value, int):
            return value

        if isinstance(value, PlaceHolder):
            return value.value if value.is_resolved else value

        return super().__new__(cls)

    def __init__(self, dependency: Optional[Dependency] = None, value: Union[int, "PlaceHolder"] = None):
        if self is value:
            return

        self.dependency = dependency

        if value is not None:
            self.value = value

    @property
    def value(self) -> Union[int, "PlaceHolder"]:
        """
        Return the value if this placeholder is resolved. Otherwise, return the placeholder itself.
        """

        if self.is_resolved:
            if self.dependency:
                if self._cache_value is None:
                    self._cache_value = self.dependency.value

                # noinspection PyTypeChecker
                return self._cache_value

            else:
                return self._value

        else:
            return self

    @value.setter
    def value(self, new_v: int):
        if not isinstance(new_v, int):
            raise TypeError(f"Placeholder#value must be a int, not '{type(new_v)}'")

        if self.is_resolved:
            raise ValueError(f"{self} is already resolved")

        else:
            self._value = new_v

    @property
    def is_resolved(self) -> bool:
        """
        If true, this placeholder is already resolved and has a integer value.
        """
        if self._value is not None or self._cache_value is not None:
            return True

        elif self.dependency:
            return self.dependency.is_resolved

        else:
            return False

    def __add__(self, other: Union[int, "PlaceHolder"]) -> Union[int, "PlaceHolder"]:
        other = PlaceHolder(value=other)

        if self.is_resolved and (isinstance(other, int) or other.is_resolved):
            return self.value + other

        if self.dependency:
            if self.dependency.operator == PlaceHolderOperator.Add:
                if isinstance(self.dependency.operands[0], int) or self.dependency.operands[0].is_resolved:
                    # (v0 + _) + o = (v0+o) + _
                    return (self.dependency.operands[0] + other) + self.dependency.operands[1]

                elif isinstance(self.dependency.operands[1], int) or self.dependency.operands[1].is_resolved:
                    # (_ + v1) + o = _ + (v1+o)
                    return self.dependency.operands[0] + (self.dependency.operands[1] + other)

            elif self.dependency.operator == PlaceHolderOperator.Sub:
                if isinstance(self.dependency.operands[0], int) or self.dependency.operands[0].is_resolved:
                    # (v0 - _) + o = (v0+o) - _
                    return (self.dependency.operands[0] + other) - self.dependency.operands[1]

                elif isinstance(self.dependency.operands[1], int) or self.dependency.operands[1].is_resolved:
                    # (_ - v1) + o = _ - (v1-o)
                    return self.dependency.operands[0] - (self.dependency.operands[1] - other)

        return PlaceHolder(Dependency(PlaceHolderOperator.Add, (self, other)))

    def __radd__(self, other: Union[int, "PlaceHolder"]) -> Union[int, "PlaceHolder"]:
        # Commutative property
        return self.__add__(other)

    def __sub__(self, other: Union[int, "PlaceHolder"]) -> Union[int, "PlaceHolder"]:
        other = PlaceHolder(value=other)

        if self.is_resolved and (isinstance(other, int) or other.is_resolved):
            return self.value - other

        if self.dependency:
            if self.dependency.operator == PlaceHolderOperator.Add:
                if isinstance(self.dependency.operands[0], int) or self.dependency.operands[0].is_resolved:
                    # (v0 + _) - o = (v0-o) + _
                    return (self.dependency.operands[0] - other) + self.dependency.operands[1]

                elif isinstance(self.dependency.operands[1], int) or self.dependency.operands[1].is_resolved:
                    # (_ + v1) - o = _ + (v1-o)
                    return self.dependency.operands[0] + (self.dependency.operands[1] - other)

            elif self.dependency.operator == PlaceHolderOperator.Sub:
                if isinstance(self.dependency.operands[0], int) or self.dependency.operands[0].is_resolved:
                    # (v0 - _) - o = (v0-o) - _
                    return (self.dependency.operands[0] - other) - self.dependency.operands[1]

                elif isinstance(self.dependency.operands[1], int) or self.dependency.operands[1].is_resolved:
                    # (_ - v1) - o = _ - (v1+o)
                    return self.dependency.operands[0] - (self.dependency.operands[1] + other)

        return PlaceHolder(Dependency(PlaceHolderOperator.Sub, (self, other)))

    def __rsub__(self, other: Union[int, "PlaceHolder"]) -> Union[int, "PlaceHolder"]:
        other = PlaceHolder(value=other)

        if self.is_resolved and (isinstance(other, int) or other.is_resolved):
            return other - self.value

        if self.dependency:
            if self.dependency.operator == PlaceHolderOperator.Add:
                if isinstance(self.dependency.operands[0], int) or self.dependency.operands[0].is_resolved:
                    # o - (v0 + _) => (o-v0) - _
                    return (other - self.dependency.operands[0]) - self.dependency.operands[1]

                elif isinstance(self.dependency.operands[1], int) or self.dependency.operands[1].is_resolved:
                    # o - (_ + v1) => (o-v1) - _
                    return (other - self.dependency.operands[1]) - self.dependency.operands[0]

            elif isinstance(self.dependency.operands[0], int) or self.dependency.operator == PlaceHolderOperator.Sub:
                if self.dependency.operands[0].is_resolved:
                    # o - (v0 - _) => (o-v0) + _
                    return (other - self.dependency.operands[0]) + self.dependency.operands[1]

                elif isinstance(self.dependency.operands[1], int) or self.dependency.operands[1].is_resolved:
                    # o - (_ - v1) => (o+v1) - _
                    return (other + self.dependency.operands[1]) - self.dependency.operands[0]

        return PlaceHolder(Dependency(PlaceHolderOperator.Sub, (other, self)))

    def __mul__(self, other: Union[int, "PlaceHolder"]) -> Union[int, "PlaceHolder"]:
        other = PlaceHolder(value=other)

        if self.is_resolved and (isinstance(other, int) or other.is_resolved):
            return self.value * other

        if self.dependency:
            if self.dependency.operator == PlaceHolderOperator.Add:
                if isinstance(self.dependency.operands[0], int) or self.dependency.operands[0].is_resolved:
                    # (v0 + _) * o = (v0*o) + _*o
                    return (self.dependency.operands[0] * other) + self.dependency.operands[1] * other

                elif isinstance(self.dependency.operands[1], int) or self.dependency.operands[1].is_resolved:
                    # (_ + v1) * o = _*o + (v1*o)
                    return self.dependency.operands[0] * other + (self.dependency.operands[1] * other)

            elif self.dependency.operator == PlaceHolderOperator.Sub:
                if isinstance(self.dependency.operands[0], int) or self.dependency.operands[0].is_resolved:
                    # (v0 - _) * o = (v0*o) - _*o
                    return (self.dependency.operands[0] * other) - self.dependency.operands[1] * other

                elif isinstance(self.dependency.operands[1], int) or self.dependency.operands[1].is_resolved:
                    # (_ - v1) * o = _*o - (v1*o)
                    return self.dependency.operands[0] * other - (self.dependency.operands[1] * other)

            elif self.dependency.operator == PlaceHolderOperator.Mul:
                if isinstance(self.dependency.operands[0], int) or self.dependency.operands[0].is_resolved:
                    # (v0 * _) * o = _*(v0*o)
                    return (self.dependency.operands[0] * other) * self.dependency.operands[1]

                elif isinstance(self.dependency.operands[1], int) or self.dependency.operands[1].is_resolved:
                    # (_ * v1) * o = _*(v1*o)
                    return self.dependency.operands[0] * (self.dependency.operands[1] * other)

        return PlaceHolder(Dependency(PlaceHolderOperator.Mul, (self, other)))

    def __rmul__(self, other: Union[int, "PlaceHolder"]) -> Union[int, "PlaceHolder"]:
        # Commutative property
        return self.__mul__(other)

    def __floordiv__(self, other: Union[int, "PlaceHolder"]) -> Union[int, "PlaceHolder"]:
        other = PlaceHolder(value=other)

        if self.is_resolved and (isinstance(other, int) or other.is_resolved):
            return self.value // other

        return PlaceHolder(Dependency(PlaceHolderOperator.FloorDiv, (self, other)))

    def __rfloordiv__(self, other: Union[int, "PlaceHolder"]) -> Union[int, "PlaceHolder"]:
        other = PlaceHolder(value=other)

        if self.is_resolved and (isinstance(other, int) or other.is_resolved):
            return other // self.value

        return PlaceHolder(Dependency(PlaceHolderOperator.FloorDiv, (other, self)))

    def __mod__(self, other: Union[int, "PlaceHolder"]) -> Union[int, "PlaceHolder"]:
        other = PlaceHolder(value=other)

        if self.is_resolved and (isinstance(other, int) or other.is_resolved):
            return self.value % other

        return PlaceHolder(Dependency(PlaceHolderOperator.Mod, (self, other)))

    def __rmod__(self, other: Union[int, "PlaceHolder"]) -> Union[int, "PlaceHolder"]:
        other = PlaceHolder(value=other)

        if self.is_resolved and (isinstance(other, int) or other.is_resolved):
            return other % self.value

        return PlaceHolder(Dependency(PlaceHolderOperator.Mod, (other, self)))

    def __int__(self):
        return PlaceHolder.force_int(self)

    def __eq__(self, other: Union[int, "PlaceHolder"]) -> bool:
        if not self.is_resolved:
            raise ValueError("First operand is unresolved placeholder. It can't be compared.")

        if isinstance(other, PlaceHolder):
            if not other.is_resolved:
                raise ValueError("Second operand is unresolved placeholder. It can't be compared.")

            return self.value == other.value

        else:
            return self.value == other

    def __ne__(self, other: Union[int, "PlaceHolder"]) -> bool:
        if not self.is_resolved:
            raise ValueError("First operand is unresolved placeholder. It can't be compared.")

        if isinstance(other, PlaceHolder):
            if not other.is_resolved:
                raise ValueError("Second operand is unresolved placeholder. It can't be compared.")

            return self.value != other.value

        else:
            return self.value != other

    def __gt__(self, other: Union[int, "PlaceHolder"]) -> bool:
        if not self.is_resolved:
            raise ValueError("First operand is unresolved placeholder. It can't be compared.")

        if isinstance(other, PlaceHolder):
            if not other.is_resolved:
                raise ValueError("Second operand is unresolved placeholder. It can't be compared.")

            return self.value > other.value

        else:
            return self.value > other

    def __lt__(self, other: Union[int, "PlaceHolder"]) -> bool:
        if not self.is_resolved:
            raise ValueError("First operand is unresolved placeholder. It can't be compared.")

        if isinstance(other, PlaceHolder):
            if not other.is_resolved:
                raise ValueError("Second operand is unresolved placeholder. It can't be compared.")

            return self.value < other.value

        else:
            return self.value < other

    def __ge__(self, other: Union[int, "PlaceHolder"]) -> bool:
        if not self.is_resolved:
            raise ValueError("First operand is unresolved placeholder. It can't be compared.")

        if isinstance(other, PlaceHolder):
            if not other.is_resolved:
                raise ValueError("Second operand is unresolved placeholder. It can't be compared.")

            return self.value >= other.value

        else:
            return self.value >= other

    def __le__(self, other: Union[int, "PlaceHolder"]) -> bool:
        if not self.is_resolved:
            raise ValueError("First operand is unresolved placeholder. It can't be compared.")

        if isinstance(other, PlaceHolder):
            if not other.is_resolved:
                raise ValueError("Second operand is unresolved placeholder. It can't be compared.")

            return self.value <= other.value

        else:
            return self.value <= other

    def __repr__(self):
        if self.is_resolved:
            return str(self.value)

        else:
            if self.dependency:
                return self.dependency.__repr__()

            else:
                return f"<{self.__class__.__name__} at {hex(id(self))}>"

    def dump(self):
        if self.dependency:
            return self.dependency.dump()

        elif self._value is not None:
            return str(self._value)

        else:
            return f"<{self.__class__.__name__} at {hex(id(self))}>"

    def _to_serializable_(self):
        if not self.is_resolved:
            raise ValueError("Unresolved placeholder can't be serialized")
        return self.value
