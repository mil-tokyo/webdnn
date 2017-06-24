import numpy as np

from webdnn.graph.operators.softmax import Softmax
from webdnn.graph.order import OrderC, OrderNC, OrderCN, OrderNHWC, OrderHWNC, OrderHWCN, OrderCNHW, \
    OrderCHWN, OrderNCHW
from webdnn.graph.variable import Variable


# FIXME 各orderをテストにわけられないか
def test_every_order():
    orders = [OrderC, OrderNC, OrderCN, OrderNHWC, OrderHWNC, OrderHWCN, OrderNCHW, OrderCNHW, OrderCHWN]

    for order in orders:
        op = Softmax("op", axis=order.axes[-1])

        x = Variable(np.arange(order.ndim) + 1, order)
        y, = op(x)
        for axis in y.order.axes:
            assert y.shape_dict[axis] == x.shape_dict[axis]
