from graph_builder.graph.operators.average_pooling_2d import AveragePooling2D
from graph_builder.graph.variable import Variable
from graph_builder.graph.variables.attributes.order import OrderNHWC, OrderNCHW


def test_call_NHWC():
    op = AveragePooling2D("op", {
        "ksize": [3, 3],
        "stride": [2, 2],
        "padding": [1, 1]
    })

    v1 = Variable((2, 10, 10, 3), OrderNHWC)
    v2, = op(v1)

    assert v2.axis_order == OrderNHWC
    assert v2.shape == [2, 5, 5, 3]


def test_call_NCHW():
    op = AveragePooling2D("op", {
        "ksize": [3, 3],
        "stride": [2, 2],
        "padding": [1, 1]
    })

    v1 = Variable((3, 2, 10, 10), OrderNCHW)
    v2, = op(v1)

    assert v2.axis_order == OrderNCHW
    assert v2.shape == [3, 2, 5, 5]
