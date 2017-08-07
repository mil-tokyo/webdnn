from webdnn.backend.webgpu.operators.im2col import Im2Col
from webdnn.graph.axis import Axis, AxisKeyDict
from webdnn.graph.order import OrderHWNC, OrderNHWC, OrderCHWN, OrderCNHW, OrderNCHW, \
    OrderHWCN
from webdnn.graph.variable import Variable

orders4 = [OrderNHWC, OrderHWNC, OrderHWCN, OrderNCHW, OrderCNHW, OrderCHWN]


def main(k, s, p, d, n, h1, w1, c1, expected_shape_dict: AxisKeyDict[int]):
    for order_x in orders4:
        op = Im2Col("im2col", ksize=k, stride=s, padding=p, dilation_rate=d)

        x = Variable((n, h1, w1, c1), OrderNHWC)
        x.change_order(order_x)

        y, = op(x)

        for axis in y.order.axes:
            assert y.shape_dict[axis] == expected_shape_dict[axis]


def test_normal():
    main(3, 1, 1, 1, 2, 3, 4, 5, AxisKeyDict([Axis.N, Axis.H, Axis.W, Axis.C], [2, 3, 4, 45]))


def test_large_stride():
    main(3, 2, 1, 1, 2, 5, 7, 3, AxisKeyDict([Axis.N, Axis.H, Axis.W, Axis.C], [2, 3, 4, 27]))


def test_no_padding():
    main(3, 1, 0, 1, 2, 5, 7, 3, AxisKeyDict([Axis.N, Axis.H, Axis.W, Axis.C], [2, 3, 5, 27]))


def test_projection():
    main(1, 1, 0, 1, 2, 5, 7, 3, AxisKeyDict([Axis.N, Axis.H, Axis.W, Axis.C], [2, 5, 7, 3]))


def test_fully_connected():
    main((5, 7), 1, 0, 1, 2, 5, 7, 3, AxisKeyDict([Axis.N, Axis.H, Axis.W, Axis.C], [2, 1, 1, 105]))


def test_dilated():
    main(3, 1, 1, 2, 2, 8, 9, 5, AxisKeyDict([Axis.N, Axis.H, Axis.W, Axis.C], [2, 6, 7, 45]))
