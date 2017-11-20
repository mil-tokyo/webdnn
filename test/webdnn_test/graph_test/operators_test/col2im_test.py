from webdnn.graph.axis import Axis, AxisKeyDict
from webdnn.graph.operators.col2im import Col2Im
from webdnn.graph.order import Order, OrderNHWC
from webdnn.graph.variable import Variable

OrderNHWKKC = Order([Axis.N, Axis.H, Axis.W, Axis.KH, Axis.KW, Axis.C])


def main(col_shape=[1, 5, 5, 3, 3, 6], col_order=OrderNHWKKC, ksize=3, stride=1, padding=1,
         expected_shape_dict: AxisKeyDict[int] = AxisKeyDict(OrderNHWC.axes, [1, 5, 5, 6])):
    op = Col2Im(None, ksize=ksize, stride=stride, padding=padding)

    x = Variable(col_shape, col_order)
    y, = op(x)

    for axis in y.order.axes:
        assert y.shape_dict[axis] == expected_shape_dict[axis]


def test_normal():
    main()


def test_large_stride():
    main(stride=2, expected_shape_dict=AxisKeyDict(OrderNHWC.axes, [1, 9, 9, 6]))


def test_no_padding():
    main(padding=0, expected_shape_dict=AxisKeyDict(OrderNHWC.axes, [1, 7, 7, 6]))


def test_projection():
    main(ksize=1, padding=0, col_shape=[1, 5, 5, 1, 1, 6], expected_shape_dict=AxisKeyDict(OrderNHWC.axes, [1, 5, 5, 6]))


def test_fully_connected():
    main(ksize=5, padding=0, col_shape=[1, 1, 1, 5, 5, 6], expected_shape_dict=AxisKeyDict(OrderNHWC.axes, [1, 5, 5, 6]))
