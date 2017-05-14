from typing import Dict

from graph_transpiler.graph.axis import Axis
from graph_transpiler.graph.operators.max_pooling_2d import MaxPooling2D
from graph_transpiler.graph.variable import Variable
from graph_transpiler.graph.variables.attributes.order import OrderNHWC, OrderNCHW, OrderCHWN, OrderHWCN, OrderHWNC, OrderCNHW


# FIXME 各orderをテストにわけられないか
def main(k, s, p, n, h1, w1, c1, expected_shape_dict: Dict[Axis, int]):
    orders = [OrderNHWC, OrderHWNC, OrderHWCN, OrderNCHW, OrderCNHW, OrderCHWN]

    for order_x in orders:
        op = MaxPooling2D(None, ksize=k, stride=s, padding=p)

        x = Variable((n, h1, w1, c1), OrderNHWC)
        x.change_order(order_x)

        y, = op(x)

        for axis in y.order.axes:
            assert y.shape_dict[axis] == expected_shape_dict[axis]


def test_normal():
    main(3, 1, 1, 2, 3, 4, 5, {
        Axis.N: 2,
        Axis.H: 3,
        Axis.W: 4,
        Axis.C: 5,
    })


def test_large_stride():
    main(3, 2, 1, 2, 5, 7, 3, {
        Axis.N: 2,
        Axis.H: 3,
        Axis.W: 4,
        Axis.C: 3,
    })


def test_no_padding():
    main(3, 1, 0, 2, 5, 7, 3, {
        Axis.N: 2,
        Axis.H: 3,
        Axis.W: 5,
        Axis.C: 3,
    })


def test_projection():
    main(1, 1, 0, 2, 5, 7, 3, {
        Axis.N: 2,
        Axis.H: 5,
        Axis.W: 7,
        Axis.C: 3,
    })


def test_fully_connected():
    main((5, 7), 1, 0, 2, 5, 7, 3, {
        Axis.N: 2,
        Axis.H: 1,
        Axis.W: 1,
        Axis.C: 3,
    })
