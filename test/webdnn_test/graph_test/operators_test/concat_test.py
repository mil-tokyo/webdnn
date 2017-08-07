import itertools

import numpy as np
from nose.tools import raises

from webdnn.graph.axis import Axis
from webdnn.graph.operators.concat import Concat
from webdnn.graph.order import Order, OrderC, OrderNC, OrderCN, OrderNHWC, OrderHWNC, OrderHWCN, OrderCNHW, OrderCHWN, OrderNCHW
from webdnn.graph.variable import Variable


def main(order1: Order, order2: Order, concat_axis: Axis):
    default_order = {
        1: OrderC,
        2: OrderNC,
        4: OrderNHWC
    }

    op = Concat(None, axis=concat_axis)
    x1 = Variable(np.arange(order1.ndim) + 1, default_order[order1.ndim])
    x2 = Variable(np.arange(order2.ndim) + 1, default_order[order2.ndim])

    x1.change_order(order1)
    x2.change_order(order2)

    y, = op(x1, x2)
    for axis in y.order.axes:
        if axis == concat_axis:
            assert y.shape_dict[axis] == x1.shape_dict[axis] + x2.shape_dict[axis]

        else:
            assert y.shape_dict[axis] == x1.shape_dict[axis]


def test_every_order():
    orders = [OrderC, OrderNC, OrderCN, OrderNHWC, OrderHWNC, OrderHWCN, OrderNCHW, OrderCNHW, OrderCHWN]
    axes = [Axis.N, Axis.H, Axis.W, Axis.C]

    for order1, order2, axis in itertools.product(orders, orders, axes):  # type: Order, Order, Axis
        if not order1.check_same_axes(order2) or axis not in order1.axes:
            continue

        main(order1, order2, axis)


@raises(AssertionError)
def test_invalid_size():
    op = Concat(None, axis=Axis.C)

    v1 = Variable((2, 3, 4, 5), OrderNHWC)
    v2 = Variable((2, 3, 7, 6), OrderNHWC)
    v3, = op(v1, v2)
