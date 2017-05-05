import itertools

import numpy as np

from graph_builder.graph.axis import Axis
from graph_builder.graph.operators.linear import Linear
from graph_builder.graph.variable import Variable
from graph_builder.graph.variables.attributes.order import OrderNC, OrderCN, OrderNHWC, OrderHWNC, OrderHWCN, OrderCNHW, \
    OrderCHWN, OrderNCHW


# FIXME 各orderをテストにわけられないか
def test_every_order():
    orders = [OrderNC, OrderCN, OrderNHWC, OrderHWNC, OrderHWCN, OrderNCHW, OrderCNHW, OrderCHWN]

    for order1, order2 in itertools.product(orders, orders):
        if set(order1.axes) != set(order2.axes):
            continue

        default_order = {
            2: OrderNC,
            4: OrderNHWC
        }

        op = Linear("op")
        x1 = Variable(np.arange(order1.ndim) + 1, default_order[order2.ndim])
        x2 = Variable(np.arange(order2.ndim) + 1, default_order[order2.ndim])

        x1.change_axis_order(order1)
        x2.change_axis_order(order2)

        y, = op(x1, x2)
        assert y.shape_dict[Axis.N] == x1.shape_dict[Axis.N]
        assert y.shape_dict[Axis.C] == x2.shape_dict[Axis.N]
