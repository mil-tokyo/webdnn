import numpy as np

from graph_builder.graph.operators.softmax import Softmax
from graph_builder.graph.variable import Variable
from graph_builder.graph.variables.attributes.order import OrderC, OrderNC, OrderCN, OrderNHWC, OrderHWNC, OrderHWCN, OrderCNHW, \
    OrderCHWN, OrderNCHW


# FIXME 各orderをテストにわけられないか
def test_every_order():
    orders = [OrderC, OrderNC, OrderCN, OrderNHWC, OrderHWNC, OrderHWCN, OrderNCHW, OrderCNHW, OrderCHWN]

    for order in orders:
        op = Softmax("op")

        x = Variable(np.arange(order.ndim) + 1, order)
        y, = op(x)
        for axis in y.axis_order.axes:
            assert y.shape_dict[axis] == x.shape_dict[axis]
