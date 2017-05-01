from graph_builder.graph.operators.constant_bias import ConstantBias
from graph_builder.graph.variable import Variable
from graph_builder.graph.variables.attributes.order import OrderNHWC, OrderNCHW


def test_call_NHWC():
    op = ConstantBias("op", {"value": 1})

    v1 = Variable((2, 3, 4, 5), OrderNHWC)
    v2, = op(v1)

    assert v2.axis_order == v1.axis_order
    assert v2.shape == v1.shape


def test_call_NCHW():
    op = ConstantBias("op", {"value": 1})

    v1 = Variable((2, 3, 4, 5), OrderNCHW)
    v2, = op(v1)

    assert v2.axis_order == v1.axis_order
    assert v2.shape == v1.shape
