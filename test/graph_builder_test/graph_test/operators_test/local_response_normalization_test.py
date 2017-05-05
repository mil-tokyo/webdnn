import numpy as np

from graph_builder.graph.operators.local_response_normalization import LocalResponseNormalization
from graph_builder.graph.variable import Variable
from graph_builder.graph.variables.attributes.order import OrderNHWC, OrderHWNC, OrderHWCN, OrderCNHW, \
    OrderCHWN, OrderNCHW


# FIXME 各orderをテストにわけられないか
def test_every_order():
    orders = [OrderNHWC, OrderHWNC, OrderHWCN, OrderNCHW, OrderCNHW, OrderCHWN]

    for order in orders:
        op = LocalResponseNormalization("op", parameters={
            "n": 1,
            "k": 2,
            "alpha": 0.1,
            "beta": 0.2
        })

        x = Variable(np.arange(order.ndim) + 1, OrderNHWC)
        x.change_axis_order(order)

        y, = op(x)

        for axis in y.axis_order.axes:
            assert y.shape_dict[axis] == x.shape_dict[axis]
