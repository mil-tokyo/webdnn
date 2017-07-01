import itertools

import numpy as np
from nose.tools import raises

from webdnn.graph.axis import Axis
from webdnn.graph.operators.axiswise_scale import AxiswiseScale
from webdnn.graph.order import OrderC, OrderNC, OrderNHWC, OrderHWNC, OrderHWCN, OrderCNHW, \
    OrderCHWN, OrderNCHW
from webdnn.graph.variable import Variable


def test_every_order():
    orders_x = [OrderNHWC, OrderHWNC, OrderHWCN, OrderNCHW, OrderCNHW, OrderCHWN]
    axes = [Axis.C]

    default_order = {
        1: OrderC,
        2: OrderNC,
        4: OrderNHWC,
        Axis.C: OrderC
    }

    for order_x, axis in itertools.product(orders_x, axes):
        if axis not in order_x.axes:
            continue

        op = AxiswiseScale(None, axis=axis)
        x = Variable(np.arange(order_x.ndim) + 1, default_order[order_x.ndim])
        x.change_order(order_x)
        w = Variable((x.shape_dict[axis],), default_order[axis])

        y, = op(x, w)

        for axis in y.order.axes:
            assert y.shape_dict[axis] == x.shape_dict[axis]


@raises(AssertionError)
def test_invalid_size():
    op = AxiswiseScale(None, axis=Axis.C)

    x = Variable((2, 3, 4, 5), OrderNHWC)
    w = Variable((6,), OrderC)
    y, = op(x, w)
