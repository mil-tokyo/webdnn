from typing import List, Union, Generic, TypeVar

from webdnn.graph.axis import Axis
from webdnn.graph.order import Order
from webdnn.graph.placeholder import Placeholder

T = TypeVar("T")


class InferenceVar(Generic[T]):
    """
    InferenceVar()

    Object to represent unknown type (like placeholder)
    """

    _counter = 0

    def __init__(self):
        self._value = None  # type: Union[T,InferenceVar[T], None]
        self._id = InferenceVar._counter
        InferenceVar._counter += 1

    @property
    def value(self) -> Union[T, None]:
        if isinstance(self._value, InferenceVar):
            return self._value.value

        else:
            return self._value

    @value.setter
    def value(self, newVal):
        if newVal == self:
            return

        elif isinstance(self._value, InferenceVar):
            self._value.value = newVal
            self._value = newVal

        else:
            self._value = newVal

    def unify(self, other: Union[T, "InferenceVar[T]"]):
        if isinstance(other, InferenceVar):
            if self.value is None and other.value is None:
                self.value = other

            elif self.value is not None:
                other.value = self.value

            elif other.value is not None:
                self.value = other.value

            else:
                assert self.value == other.value, "Unification failed"

        else:
            if self.value is None:
                self.value = other

            else:
                assert self.value == other, "Unification failed"


class AxisVar(InferenceVar[Axis]):
    @property
    def name(self):
        return self._value.name if self._value is not None else f"?{str(self._id)}"

    def __eq__(self, other):
        # noinspection PyBroadException
        try:
            return other.name == self.name

        except Exception:
            return False

    __hash__ = None


T = TypeVar("T")


def unify(v1: Union[T, InferenceVar[T]], v2: Union[T, InferenceVar[T]]):
    if isinstance(v1, InferenceVar):
        v1.unify(v2)

    elif isinstance(v2, InferenceVar):
        v2.unify(v1)

    else:
        assert v1 == v2, f"Unification failed: (v1)={v1}, (v2)={v2}"


def unify_order(order1: Order, order2: Order):
    assert order1.ndim == order2.ndim, f"Unification failed: (order1.ndim)={order1.ndim}, (order2.ndim)={order2.ndim}"
    for axis1, axis2 in zip(order1.axes, order2.axes):
        unify(axis1, axis2)


def add_placeholder_constraint(p1: Union[int, Placeholder], p2: Union[int, Placeholder]):
    if Placeholder.check_resolved(p1) and Placeholder.check_resolved(p2):
        assert Placeholder.force_int(p1) == Placeholder.force_int(p2), f"Conflict is detected: " \
                                                                       f"(p1)={Placeholder.force_int(p1)}, " \
                                                                       f"(p2)={Placeholder.force_int(p2)}"

    elif Placeholder.check_resolved(p1) and not Placeholder.check_resolved(p2):
        p2.value = Placeholder.force_int(p1)

    elif not Placeholder.check_resolved(p1) and Placeholder.check_resolved(p1):
        p1.value = Placeholder.force_int(p2)


def add_shape_constraint(shape1: List[Union[int, Placeholder]], shape2: List[Union[int, Placeholder]]):
    assert len(shape1) == len(shape2), f"Conflict is detected: (shape1.ndim)={len(shape1)}, (shape2.ndim)={len(shape2)})"

    for p1, p2 in zip(shape1, shape2):
        add_placeholder_constraint(p1, p2)
