from nose.tools import raises

from graph_builder.graph.axis import Axis
from graph_builder.graph.operators.axiswise_scale import AxiswiseScale
from graph_builder.graph.variable import Variable
from graph_builder.graph.variables.attributes.order import OrderNHWC, OrderC, OrderNCHW


def test_call_NHWC():
    op = AxiswiseScale("op", {"axis": Axis.C})

    v1 = Variable((2, 3, 4, 5), OrderNHWC)
    w = Variable((5,), OrderC)
    v2, = op(v1, w)

    assert v2.axis_order == OrderNHWC
    assert v2.shape == [2, 3, 4, 5]


def test_call_NCHW():
    op = AxiswiseScale("op", {"axis": Axis.C})

    v1 = Variable((2, 3, 4, 5), OrderNCHW)
    w = Variable((3,), OrderC)
    v2, = op(v1, w)

    assert v2.axis_order == OrderNCHW
    assert v2.shape == [2, 3, 4, 5]


@raises(AssertionError)
def test_call_invalid_size():
    op = AxiswiseScale("op", {"axis": Axis.C})

    v1 = Variable((2, 3, 4, 5), OrderNHWC)
    w = Variable((6,), OrderC)
    v2, = op(v1, w)


@raises(AssertionError)
def test_call_invalid_axis():
    op = AxiswiseScale("op", {"axis": Axis.N})

    v1 = Variable((2, 3, 4, 5), OrderNHWC)
    w = Variable((5,), OrderC)
    v2, = op(v1, w)
