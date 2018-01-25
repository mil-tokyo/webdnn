from typing import Optional, Union, Sequence, Tuple, List

from webdnn.graph.axis import Axis, AxisKeyDict
from webdnn.graph.operator import Operator
from webdnn.graph.operators.attributes.tensorwise import Tensorwise
from webdnn.graph.order import Order
from webdnn.graph.variable import Variable
from webdnn.util.misc import mul

_AxisSequence = Sequence[Axis]


def _normalize_axes(axes: Union[Axis, Sequence[Union[Axis, Sequence[Axis]]]]) -> Tuple[Tuple[Axis, ...], Tuple[Axis, ...]]:
    if isinstance(axes, Axis):
        return (axes,), (axes,)

    elif isinstance(axes, Sequence):
        assert len(axes) == 2, f"""
[Tensordot] When the argument "axes" is sequence, its length must be 2:
    (axes) = {axes}
    (len(axes)) = {len(axes)}"""

        ret = []  # type: List[Tuple[Axis, ...]]
        for i, a in enumerate(axes):
            if isinstance(a, Axis):
                ret.append((a,))

            elif isinstance(a, Sequence):
                for j, aa in enumerate(a):
                    if not isinstance(aa, Axis):
                        raise TypeError(f"""
[Tensordot] When the argument "axes" is sequence, its contents must be instance of axis or sequence of axis:
    (axes) = {axes}
    (type(axes[{i}][{j}])) = {type(axes[i][j]).__name__}""")
                ret.append(tuple(a))

            else:
                raise TypeError(f"""
[Tensordot] When the argument "axes" is sequence, its contents must be instance of axis or sequence of axis:
    (axes) = {axes}
    (type(axes[{i}])) = {type(axes[i]).__name__}""")

        ret = tuple(ret)  # type: Tuple[Tuple[Axis, ...], Tuple[Axis, ...]]
        return ret

    else:
        raise TypeError(f"""
[Tensordot] Argument "axes" must be an instance of axis or sequence of axis.
    (axes) = {axes}
    (type(axes)) = {type(axes).__name__}""")


class Tensordot(Operator):
    """Tensordot(name, axes)

    Tensordot operator

    Args:
        name (str): Operator name.
        axes (:class:`~Axis`, list of :class:`~Axis`, list of list of :class:`~Axis`): axes which are reduced
            If `axes` is an :class:`~Axis` instance,

    Signature
        .. code::

            C, = op(A, B)

        - **A**, **B** - Input variables.
        - **C** - Output variable.
    """

    def __init__(self, name: Optional[str], axes: Union[Axis, Sequence[Union[Axis, Sequence[Axis]]]]):
        super().__init__(name)

        self.parameters["axes"] = _normalize_axes(axes)

    def __call__(self, A: Variable, B: Variable):
        for axis in self.axes[0]:
            assert axis in A.order.axes, f"""
[Tensordot] Input variable "A" must have axes "{axis}":
    (op) = {self}
    (op.axes[0]) = {self.axes[0]}
    (A) = {A}"""

        for axis in A.order.axes:
            if axis not in self.axes[0]:
                assert axis in self.axes[1] or axis not in B.order.axes, f"""
[Tensordot] Axes of "A" which are not reduced must not be contained in "B":
    (op) = {self}
    (A.order.axes) = {A.order.axes}
    (B.order.axes) = {B.order.axes}
    (op.axes) = {self.axes}"""

        for axis in self.axes[1]:
            assert axis in B.order.axes, f"""
[Tensordot] Input variable "B" must have axes "{axis}":
    (op) = {self}
    (op.axes[1]) = {self.axes[1]}
    (B) = {B}"""

        for axis in B.order.axes:
            if axis not in self.axes[1]:
                assert axis in self.axes[0] or axis not in A.order.axes, f"""
[Tensordot] Axes of "B" which are not reduced must not be contained in "A":
    (op) = {self}
    (A.order.axes) = {A.order.axes}
    (B.order.axes) = {B.order.axes}
    (op.axes) = {self.axes}"""

        reduction_size_a = mul(A.shape_dict[a] for a in self.axes[0])
        reduction_size_b = mul(B.shape_dict[a] for a in self.axes[1])
        assert reduction_size_a == reduction_size_b, f"""
[Tensordot] Reduction size of "A" and "B" must be same:
    (A) = {A}
    (B) = {B}
    (axes) = {self.axes}
    (reduction size of A) = {reduction_size_a}
    (reduction size of B) = {reduction_size_b}
"""

        c_shape_dict = AxisKeyDict()

        for axis in A.order.axes:
            if axis not in self.axes[0]:
                c_shape_dict[axis] = A.shape_dict[axis]

        for axis in B.order.axes:
            if axis not in self.axes[1]:
                c_shape_dict[axis] = B.shape_dict[axis]

        C = Variable(list(c_shape_dict.values()), Order(list(c_shape_dict.keys())))

        for axis in C.order.axes:
            self.attributes.add(Tensorwise(axis))

        self.append_input("A", A)
        self.append_input("B", B)
        self.append_output("C", C)
        return C,

    @property
    def axes(self) -> Tuple[Tuple[Axis, ...], Tuple[Axis, ...]]:
        return self.parameters["axes"]
