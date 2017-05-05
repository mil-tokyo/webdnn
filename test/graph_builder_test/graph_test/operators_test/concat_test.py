import itertools
from typing import Type

import numpy as np
from nose.tools import raises

from graph_builder.graph.axis import Axis
from graph_builder.graph.operators.concat import Concat
from graph_builder.graph.variable import Variable
from graph_builder.graph.variables.attributes.order import AxisOrder, OrderC, OrderNC, OrderCN, OrderNHWC, OrderHWNC, OrderHWCN, OrderCNHW, \
    OrderCHWN, OrderNCHW


def main(order1: Type[AxisOrder], order2: Type[AxisOrder], concat_axis: Axis):
    default_order = {
        1: OrderC,
        2: OrderNC,
        4: OrderNHWC
    }

    op = Concat("op", {"axis": concat_axis})
    x1 = Variable(np.arange(order1.ndim) + 1, default_order[order1.ndim])
    x2 = Variable(np.arange(order2.ndim) + 1, default_order[order2.ndim])

    x1.change_axis_order(order1)
    x2.change_axis_order(order2)

    y, = op(x1, x2)
    for axis in y.axis_order.axes:
        if axis == concat_axis:
            assert y.shape_dict[axis] == x1.shape_dict[axis] + x2.shape_dict[axis]

        else:
            assert y.shape_dict[axis] == x1.shape_dict[axis]


# FIXME 各orderをテストにわけられないか
def test_every_order():
    orders = [OrderC, OrderNC, OrderCN, OrderNHWC, OrderHWNC, OrderHWCN, OrderNCHW, OrderCNHW, OrderCHWN]
    axes = [Axis.N, Axis.H, Axis.W, Axis.C]

    for order1, order2, axis in itertools.product(orders, orders, axes):
        if set(order1.axes) != set(order2.axes) or axis not in order1.axes:
            continue

        main(order1, order2, axis)


@raises(AssertionError)
def test_invalid_size():
    op = Concat("op", {"axis": Axis.C})

    v1 = Variable((2, 3, 4, 5), OrderNHWC)
    v2 = Variable((2, 3, 7, 6), OrderNHWC)
    v3, = op(v1, v2)
