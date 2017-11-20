from webdnn.graph.axis import Axis, AxisKeyDict
from webdnn.graph.operators.im2col import Im2Col
from webdnn.graph.order import Order, OrderNHWC
from webdnn.graph.variable import Variable

OrderNHWKKC = Order([Axis.N, Axis.H, Axis.W, Axis.KH, Axis.KW, Axis.C])


def main(im_shape=[1, 5, 5, 6], im_order=OrderNHWC, ksize=3, stride=1, padding=1, dilation_rate=1,
         expected_shape_dict: AxisKeyDict[int] = AxisKeyDict(OrderNHWKKC.axes, [1, 5, 5, 3, 3, 6])):
    op = Im2Col(None, ksize=ksize, stride=stride, padding=padding, dilation_rate=dilation_rate)

    x = Variable(im_shape, im_order)
    y, = op(x)

    for axis in y.order.axes:
        assert y.shape_dict[axis] == expected_shape_dict[axis]


def test_normal():
    main()


def test_large_stride():
    main(stride=2, im_shape=[1, 9, 9, 6], expected_shape_dict=AxisKeyDict(OrderNHWKKC.axes, [1, 5, 5, 3, 3, 6]))


def test_no_padding():
    main(padding=0, expected_shape_dict=AxisKeyDict(OrderNHWKKC.axes, [1, 3, 3, 3, 3, 6]))


def test_projection():
    main(ksize=1, padding=0, expected_shape_dict=AxisKeyDict(OrderNHWKKC.axes, [1, 5, 5, 1, 1, 6]))


def test_fully_connected():
    main(ksize=5, padding=0, expected_shape_dict=AxisKeyDict(OrderNHWKKC.axes, [1, 1, 1, 5, 5, 6]))


def test_dilated():
    main(ksize=3, dilation_rate=2, expected_shape_dict=AxisKeyDict(OrderNHWKKC.axes, [1, 3, 3, 3, 3, 6]))
