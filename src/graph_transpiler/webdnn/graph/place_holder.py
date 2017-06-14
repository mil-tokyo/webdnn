from enum import auto, Enum
from typing import Union, Optional, List

import numpy as np

from webdnn.util.json import json


class PlaceHolderOperator(Enum):
    Add = auto()  # v1 + v2
    Sub = auto()  # v1 - v2
    Mul = auto()  # v1 * v2
    Mod = auto()  # v1 % v2
    FloorDiv = auto()  # v1 // v2


class Dependency:
    operator: PlaceHolderOperator
    operands: List[Union[int, "PlaceHolder"]]

    def __init__(self, operator: PlaceHolderOperator, operands: List[Union[int, "PlaceHolder"]]):
        self.operator = operator
        operands = list(operands)

        if operator == PlaceHolderOperator.Add:
            i = 0
            while i < len(operands):
                v1 = operands[i]
                j = i + 1
                while j < len(operands):
                    v2 = operands[j]

                    # v = ... + v1 + v2 + ...
                    # v1 = common_term * other_term1
                    # v2 = common_term * other_term2
                    #
                    #
                    # >> When other_term1 and other_term2 are resolved,
                    #
                    # v = (... + (other_term1 + other_term2) * common_term + ...)
                    other_term1 = list(v1.dependency.operands) if v1.dependency else {v1}
                    other_term2 = list(v2.dependency.operands) if v2.dependency else {v2}
                    common_term = list()

                    for vv in list(other_term1):
                        if vv in other_term2:
                            other_term1.remove(vv)
                            other_term2.remove(vv)
                            common_term.append(vv)

                    for vv in list(other_term2):
                        if vv in other_term1:
                            other_term1.remove(vv)
                            other_term2.remove(vv)
                            common_term.append(vv)

                    if all(p.is_resolved for p in other_term1) and all(p.is_resolved for p in other_term2):
                        other_term1 = PlaceHolder(Dependency(PlaceHolderOperator.Mul, list(other_term1)))
                        other_term2 = PlaceHolder(Dependency(PlaceHolderOperator.Mul, list(other_term2)))
                        common_term = PlaceHolder(Dependency(PlaceHolderOperator.Mul, list(common_term)))
                        operands.pop(j)
                        operands.pop(i)
                        j -= 1
                        i -= 1
                        operands.append(PlaceHolder(value=(other_term1 + other_term2) * common_term))

                    j += 1
                i += 1

        elif operator == PlaceHolderOperator.Mul:
            s = 1
            i = 0
            while i < len(operands):
                v1 = operands[i]
                if v1.is_resolved:
                    s *= v1
                    operands.pop(i)
                    i -= 1
                i += 1

            if s != 1:
                operands.append(PlaceHolder(value=s))

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
            r = 0
            for v in self.operands:
                r += v.value
            return r

        elif self.operator == PlaceHolderOperator.Sub:
            raise NotImplementedError

        elif self.operator == PlaceHolderOperator.Mul:
            r = 1
            for v in self.operands:
                r *= v.value
            return r

        elif self.operator == PlaceHolderOperator.Mod:
            return self.operands[0].value % self.operands[1].value

        elif self.operator == PlaceHolderOperator.FloorDiv:
            return self.operands[0].value // self.operands[1].value

        else:
            raise NotImplementedError(f"Unsupported placeholder operation: {self.operator}")

    def __repr__(self):
        if self.operator == PlaceHolderOperator.Add:
            return " + ".join(map(lambda x: x.__repr__(), self.operands))

        elif self.operator == PlaceHolderOperator.Sub:
            return " - ".join(map(lambda x: x.__repr__(), self.operands))

        s = []
        for v in self.operands:
            if v.dependency and len(v.dependency.operands) > 1:
                s.append("(" + v.__repr__() + ")")
            else:
                s.append(v.__repr__())

        if self.operator == PlaceHolderOperator.Mul:
            return " * ".join(s)

        elif self.operator == PlaceHolderOperator.Mod:
            return " % ".join(s)

        elif self.operator == PlaceHolderOperator.FloorDiv:
            return " // ".join(s)

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

    def generate_js_function(self):
        if self.operator == PlaceHolderOperator.Add:
            return " + ".join(map(lambda x: x.generate_js_function(flag_semicolon=False), self.operands))

        elif self.operator == PlaceHolderOperator.Sub:
            return " - ".join(map(lambda x: x.generate_js_function(flag_semicolon=False), self.operands))

        s = []
        for v in self.operands:
            if v.dependency and len(v.dependency.operands) > 1:
                s.append("(" + v.generate_js_function(flag_semicolon=False) + ")")
            else:
                s.append(v.generate_js_function(flag_semicolon=False))

        if self.operator == PlaceHolderOperator.Mul:
            return " * ".join(s)

        elif self.operator == PlaceHolderOperator.Mod:
            return " % ".join(s)

        elif self.operator == PlaceHolderOperator.FloorDiv:
            assert len(s) == 2
            return f"Math.floor({s[0]} / {s[1]})"

        raise NotImplementedError(f"Unsupported placeholder operation: {self.operator}")


_id = 0


class PlaceHolder(json.SerializableMixin):
    _value: Optional[int] = None
    _cache_value = None
    label: Optional[str] = None
    dependency: Optional[Dependency] = None

    @staticmethod
    def to_int(x: Union[int, "PlaceHolder"]):
        if isinstance(x, PlaceHolder):
            return x.value if x.is_resolved else x

        else:
            return int(x)

    @staticmethod
    def force_int(x: Union[int, "PlaceHolder"]):
        if isinstance(x, PlaceHolder):
            if x.is_resolved:
                return x.value

            raise ValueError(f"{x} is not resolved.")
        else:
            return int(x)

    @staticmethod
    def check_resolved(x: Union[int, "PlaceHolder"]):
        if isinstance(x, PlaceHolder):
            return x.is_resolved

        else:
            return True

    def __new__(cls, dependency: Optional[Dependency] = None, value: Union[int, "PlaceHolder"] = None, label: str = None):
        if isinstance(value, PlaceHolder):
            return value

        return super().__new__(cls)

    def __init__(self, dependency: Optional[Dependency] = None, value: Union[int, "PlaceHolder"] = None, label: Optional[str] = None):
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
        if not (isinstance(new_v, int) or isinstance(new_v, np.int32) or isinstance(new_v, np.int64)):
            raise TypeError(f"Placeholder#value must be a int, not '{type(new_v)}'")

        if self.is_resolved:
            raise ValueError(f"{self} is already resolved")

        else:
            # noinspection PyTypeChecker
            self._value = int(new_v)

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

        if self.is_resolved and other.is_resolved:
            return self.value + other.value

        if self.dependency:
            if self.dependency.operator == PlaceHolderOperator.Add:
                return PlaceHolder(Dependency(PlaceHolderOperator.Add, self.dependency.operands + [other]))

        return PlaceHolder(Dependency(PlaceHolderOperator.Add, [self, other]))

    def __radd__(self, other: Union[int, "PlaceHolder"]) -> Union[int, "PlaceHolder"]:
        # Commutative property
        return self.__add__(other)

    def __sub__(self, other: Union[int, "PlaceHolder"]) -> Union[int, "PlaceHolder"]:
        return self + (-1 * other)

    def __rsub__(self, other: Union[int, "PlaceHolder"]) -> Union[int, "PlaceHolder"]:
        return (-1 * self) + other

    def __mul__(self, other: Union[int, "PlaceHolder"]) -> Union[int, "PlaceHolder"]:
        other = PlaceHolder(value=other)

        if self.is_resolved and other.is_resolved:
            return self.value * other.value

        if self.dependency:
            if self.dependency.operator == PlaceHolderOperator.Add or self.dependency.operator == PlaceHolderOperator.Sub:
                # (v0+v1)*o = v0*o + v1*o
                return PlaceHolder(Dependency(self.dependency.operator, [PlaceHolder(value=v * other) for v in self.dependency.operands]))

            elif self.dependency.operator == PlaceHolderOperator.Mul:
                return PlaceHolder(Dependency(PlaceHolderOperator.Mul, self.dependency.operands + [other]))

        return PlaceHolder(Dependency(PlaceHolderOperator.Mul, [self, other]))

    def __rmul__(self, other: Union[int, "PlaceHolder"]) -> Union[int, "PlaceHolder"]:
        return self.__mul__(other)

    def __floordiv__(self, other: Union[int, "PlaceHolder"]) -> Union[int, "PlaceHolder"]:
        other = PlaceHolder(value=other)

        if self.is_resolved and other.is_resolved:
            return self.value // other.value

        return PlaceHolder(Dependency(PlaceHolderOperator.FloorDiv, [self, other]))

    def __rfloordiv__(self, other: Union[int, "PlaceHolder"]) -> Union[int, "PlaceHolder"]:
        other = PlaceHolder(value=other)

        if self.is_resolved and other.is_resolved:
            return other.value // self.value

        return PlaceHolder(Dependency(PlaceHolderOperator.FloorDiv, [other, self]))

    def __mod__(self, other: Union[int, "PlaceHolder"]) -> Union[int, "PlaceHolder"]:
        other = PlaceHolder(value=other)

        if self.is_resolved and other.is_resolved:
            return self.value % other.value

        return PlaceHolder(Dependency(PlaceHolderOperator.Mod, [self, other]))

    def __rmod__(self, other: Union[int, "PlaceHolder"]) -> Union[int, "PlaceHolder"]:
        other = PlaceHolder(value=other)

        if self.is_resolved and other.is_resolved:
            return other.value % self.value

        return PlaceHolder(Dependency(PlaceHolderOperator.Mod, [other, self]))

    def __int__(self):
        return PlaceHolder.force_int(self)

    def __eq__(self, other: Union[int, "PlaceHolder"]) -> bool:
        if not self.is_resolved or not PlaceHolder.check_resolved(other):
            return id(self) == id(other)

        return self.value == PlaceHolder.force_int(other)

    def __ne__(self, other: Union[int, "PlaceHolder"]) -> bool:
        if not self.is_resolved or not PlaceHolder.check_resolved(other):
            return id(self) != id(other)

        return self.value != PlaceHolder.force_int(other)

    def __gt__(self, other: Union[int, "PlaceHolder"]) -> bool:
        if not self.is_resolved:
            raise ValueError("First operand is unresolved placeholder. It can't be compared.")

        if not PlaceHolder.check_resolved(other):
            raise ValueError("Second operand is unresolved placeholder. It can't be compared.")

        return self.value > PlaceHolder.force_int(other)

    def __lt__(self, other: Union[int, "PlaceHolder"]) -> bool:
        if not self.is_resolved:
            raise ValueError("First operand is unresolved placeholder. It can't be compared.")

        if not PlaceHolder.check_resolved(other):
            raise ValueError("Second operand is unresolved placeholder. It can't be compared.")

        return self.value < PlaceHolder.force_int(other.value)

    def __ge__(self, other: Union[int, "PlaceHolder"]) -> bool:
        if not self.is_resolved:
            raise ValueError("First operand is unresolved placeholder. It can't be compared.")

        if not PlaceHolder.check_resolved(other):
            raise ValueError("Second operand is unresolved placeholder. It can't be compared.")

        return self.value >= PlaceHolder.force_int(other)

    def __le__(self, other: Union[int, "PlaceHolder"]) -> bool:
        if not self.is_resolved:
            raise ValueError("First operand is unresolved placeholder. It can't be compared.")

        if not PlaceHolder.check_resolved(other):
            raise ValueError("Second operand is unresolved placeholder. It can't be compared.")

        return self.value <= PlaceHolder.force_int(other)

    def __repr__(self):
        if self.is_resolved:
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
        if self.is_resolved:
            return self.value

        else:
            return {
                "eval": self.generate_js_function()
            }

    def get_depend_placeholders(self):
        if PlaceHolder.check_resolved(self):
            return set()

        if self.dependency:
            res = set()
            for v in self.dependency.operands:
                res.update(v.get_depend_placeholders())
            return res

        else:
            return {self}

    def generate_js_function(self, flag_semicolon=True):
        if self.is_resolved:
            return f"{self.value}" + (";" if flag_semicolon else "")

        else:
            if self.dependency:
                return self.dependency.generate_js_function()

            else:
                return f"placeholders['{self.label}']"
