import itertools

import numpy as np

from webdnn.graph.axis import Axis
from webdnn.graph.operators.linear import Linear
from webdnn.graph.order import Order
from webdnn.graph.order import OrderNC, OrderCN, OrderNHWC, OrderHWNC, OrderHWCN, OrderCNHW, \
    OrderCHWN, OrderNCHW
from webdnn.graph.variable import Variable


def test_every_order():
    orders = [OrderNC, OrderCN, OrderNHWC, OrderHWNC, OrderHWCN, OrderNCHW, OrderCNHW, OrderCHWN]

    for order1, order2 in itertools.product(orders, orders):  # type: Order, Order
        if not order1.check_same_axes(order2):
            continue

        default_order = {
            2: OrderNC,
            4: OrderNHWC
        }

        op = Linear("op")
        x1 = Variable(np.arange(order1.ndim) + 1, default_order[order2.ndim])
        x2 = Variable(np.arange(order2.ndim) + 1, default_order[order2.ndim])

        x1.change_order(order1)
        x2.change_order(order2)

        y, = op(x1, x2)
        assert y.shape_dict[Axis.N] == x1.shape_dict[Axis.N]
        assert y.shape_dict[Axis.C] == x2.shape_dict[Axis.N]
