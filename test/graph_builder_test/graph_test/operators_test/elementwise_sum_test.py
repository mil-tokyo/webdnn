import itertools

import numpy as np
from nose.tools import raises

from graph_transpiler.graph.operators.elementwise_sum import ElementwiseSum
from graph_transpiler.graph.variable import Variable
from graph_transpiler.graph.variables.attributes.order import OrderC, OrderNC, OrderCN, OrderNHWC, OrderHWNC, OrderHWCN, OrderCNHW, \
    OrderCHWN, OrderNCHW


# FIXME 各orderをテストにわけられないか
def test_every_order():
    orders = [OrderC, OrderNC, OrderCN, OrderNHWC, OrderHWNC, OrderHWCN, OrderNCHW, OrderCNHW, OrderCHWN]

    for order1, order2 in itertools.product(orders, orders):
        if set(order1.axes) != set(order2.axes):
            continue

        default_order = {
            1: OrderC,
            2: OrderNC,
            4: OrderNHWC
        }

        op = ElementwiseSum("op")
        x1 = Variable(np.arange(order1.ndim) + 1, default_order[order2.ndim])
        x2 = Variable(np.arange(order2.ndim) + 1, default_order[order2.ndim])

        x1.change_order(order1)
        x2.change_order(order2)

        y, = op(x1, x2)
        for axis in order1.axes:
            assert y.shape_dict[axis] == x1.shape_dict[axis]


@raises(AssertionError)
def test_invalid_shape1():
    op = ElementwiseSum("op")

    x1 = Variable((2, 3, 4, 5), OrderNCHW)
    x2 = Variable((2, 3, 4, 6), OrderNCHW)
    y, = op(x1, x2)


@raises(AssertionError)
def test_invalid_shape2():
    op = ElementwiseSum("op")

    x1 = Variable((2, 3, 4, 5), OrderNCHW)
    x2 = Variable((2, 3, 4, 5), OrderNHWC)
    y, = op(x1, x2)
