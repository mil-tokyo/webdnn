import numpy as np
from nose.tools import raises

from graph_builder.graph.axis import Axis
from graph_builder.graph.operators.axiswise_scale import AxiswiseScale
from graph_builder.graph.variable import Variable
from graph_builder.graph.variables.attributes.order import OrderC, OrderNC, OrderCN, OrderNHWC, OrderHWNC, OrderHWCN, OrderCNHW, \
    OrderCHWN, OrderNCHW


# FIXME 各orderをテストにわけられないか
def test_every_order():
    for order in [OrderC,
                  OrderNC,
                  OrderCN,
                  OrderNHWC,
                  OrderHWNC,
                  OrderHWCN,
                  OrderNCHW,
                  OrderCNHW,
                  OrderCHWN]:
        for axis in [Axis.C]:
            default_order = {
                1: OrderC,
                2: OrderNC,
                4: OrderNHWC,
                Axis.C: OrderC
            }

            op = AxiswiseScale("op", {"axis": axis})
            x = Variable(np.arange(order.ndim) + 1, default_order[order.ndim])
            w = Variable((x.shape_dict[axis],), default_order[axis])

            y, = op(x, w)

            for axis in y.axis_order.axes:
                assert y.shape_dict[axis] == x.shape_dict[axis]


@raises(AssertionError)
def test_invalid_size():
    op = AxiswiseScale("op", {"axis": Axis.C})

    x = Variable((2, 3, 4, 5), OrderNHWC)
    w = Variable((6,), OrderC)
    y, = op(x, w)
