from typing import Optional

from webdnn.graph.axis import Axis
from webdnn.graph.variable import Variable


def check_broadcast_constraints(a: Variable, b: Variable, axis: Optional[int] = None):
    """check_broadcast_constraints(a, b, axis=None)

    Check follow constraints corresponding to broadcasting:

        - each axes pair must be same axis.
        - shape must be valid for broadcasting.

    Args:
        a: Variable
        b: Variable
        axis: broadcast start position

            a.shape=(2, 3, 4, 5) b.shape=(5),     --> If axis=3 (or None), broadcasting is possible.
            a.shape=(2, 3, 4, 5) b.shape=(3, 4),  --> If axis=1, broadcasting is possible.

        Note that `axis=None` (or `a.ndim - b.ndim`) is same as numpy-style broadcasting.

    Returns:

    """
    a_shape = list(a.shape)
    b_shape = list(b.shape)
    a_axes = list(a.order.axes)
    b_axes = list(b.order.axes)
    a_ndim = a.ndim
    b_ndim = b.ndim

    if axis is None:
        axis = a_ndim - b_ndim

    for _ in range(axis):
        b_shape = [1] + b_shape
        b_axes = [Axis()] + b_axes
        b_ndim += 1

    while a_ndim < b_ndim:
        a_shape = a_shape + [1]
        a_axes = a_axes + [Axis()]
        a_ndim += 1

    while b_ndim < a_ndim:
        b_shape = b_shape + [1]
        b_axes = b_axes + [Axis()]
        b_ndim += 1

    for i in range(a_ndim):
        if a_shape[i] == b_shape[i] or a_shape[i] == 1 or b_shape[i] == 1:
            a_axes[i].unify(b_axes[i])

            if (a_shape[i] == 1 and b_shape[i] == 1) or (a_shape[i] != 1 and b_shape[i] != 1):
                # If broadcast is not occurred, size must be same
                assert a_shape[i] == b_shape[i], f"""
Shape mismatch: a.shape[{i}] != b.shape[{i}]
  (a.shape) = {a_shape}
  (b.shape) = {b_shape}
"""

        else:
            raise ValueError(f"""Broadcast is failed: \n
  (a.shape)={a_shape}
  (b.shape)={b_shape}
  (axis)={axis}""")
