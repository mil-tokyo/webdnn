import numpy as np

from webdnn.graph.operators.scalar_affine import ScalarAffine
from webdnn.graph.order import OrderHWNC, OrderNHWC, OrderCN, OrderNC, OrderC, OrderCHWN, OrderCNHW, OrderNCHW, \
    OrderHWCN
from webdnn.graph.variable import Variable


# FIXME: use template_elementwise_operator
def test_every_order():
    orders = [OrderC, OrderNC, OrderCN, OrderNHWC, OrderHWNC, OrderHWCN, OrderNCHW, OrderCNHW, OrderCHWN]

    for order in orders:
        op = ScalarAffine(None, scale=1, bias=0)

        x = Variable(np.arange(order.ndim) + 1, order)
        y, = op(x)
        for axis in y.order.axes:
            assert y.shape_dict[axis] == x.shape_dict[axis]
