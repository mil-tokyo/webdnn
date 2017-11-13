import itertools
from typing import Tuple, Sequence, Union

from webdnn.graph.axis import Axis, AxisKeyDict, UnificationFailedError


class Order:
    """Order(axes)

    Descriptor class for representing semantics of data order.

    For example, :obj:`~webdnn.graph.order.OrderNHWC` means that the data is aligned as Channel-major (Batch-size-minor).
    Popular data order is already defined in :mod:`webdnn.graph.order`. You should use pre-defined order instance.

    If you have to define new data order, you can simply as follows.

    .. code::

        OrderHCNW = Order([Axis.H, Axis.C, Axis.N, Axis.W])

    Args:
        axes(list of :class:`~webdnn.Axis`): list of axis.
    """

    def __init__(self, axes: Sequence[Union[Axis, None]]):
        axes = tuple(Axis() if a is None else a for a in axes)
        for a1, a2 in itertools.permutations(axes, 2):
            assert a1 != a2, f"""
[Order] Axes are duplicated:
    (axes) = {axes}
"""
        self._axes = axes

    @property
    def axes(self) -> Tuple[Axis, ...]:
        return self._axes

    @property
    def ndim(self) -> int:
        return len(self.axes)

    @property
    def axes_dict(self) -> AxisKeyDict[int]:
        return AxisKeyDict(self.axes, range(self.ndim))

    def __eq__(self, other):
        if isinstance(other, Order):
            return self.axes == other.axes

        else:
            return False

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"[{', '.join([axis.name for axis in self.axes])}]"

    def check_same_axes(self, other: "Order") -> bool:
        """
        check_same_axes(order)

        check if 2 orders have same axes (the axis order is not considered)

        Args:
            other: other order
        """
        return all(axis in other.axes for axis in self.axes) and all(axis in self.axes for axis in other.axes)

    def get_common_axes(self, other: "Order") -> Sequence[Axis]:
        """
        get_common_axes(order)

        return axes which are included in both two order.

        Args:
            other: other order
        """
        return [axis for axis in self.axes if axis in other.axes]

    def get_all_axes(self, other: "Order") -> Sequence[Axis]:
        """
        get_all_axes(order)

        return axes which are included in either two order.

        Args:
            other: other order
        """
        return list(self.axes) + [axis for axis in other.axes if axis not in self.axes]

    def unify(self, other: "Order"):
        if self.ndim != other.ndim:
            raise UnificationFailedError(f"""
Unification failed: Number of dimension mismatch 
    (self.ndim) = {self.ndim}
    (other.ndim) = {other.ndim}""")

        for (i, axis1), axis2 in zip(enumerate(self.axes), other.axes):
            try:
                axis1.unify(axis2)

            except UnificationFailedError:
                raise UnificationFailedError(f"""
Unification failed: self.axes[{i}] != other.axes[{i}]
    (self) = {self}
    (other) = {other}""")
