from nose.tools import raises

from graph_builder.graph.axis import Axis
from graph_builder.graph.operators.concat import Concat
from graph_builder.graph.variable import Variable
from graph_builder.graph.variables.attributes.order import OrderNHWC, OrderNCHW


def test_call_NHWC():
    op = Concat("op", {"axis": Axis.C})

    v1 = Variable((2, 3, 4, 5), OrderNHWC)
    v2 = Variable((2, 3, 4, 6), OrderNHWC)
    v3, = op(v1, v2)

    assert v3.axis_order == OrderNHWC
    assert v3.shape == [2, 3, 4, 11]


def test_call_NCHW():
    op = Concat("op", {"axis": Axis.C})

    v1 = Variable((2, 3, 4, 5), OrderNCHW)
    v2 = Variable((2, 6, 4, 5), OrderNCHW)
    v3, = op(v1, v2)

    assert v3.axis_order == OrderNCHW
    assert v3.shape == [2, 9, 4, 5]


def test_call_mix_order():
    op = Concat("op", {"axis": Axis.C})

    v1 = Variable((2, 3, 4, 5), OrderNCHW)
    v2 = Variable((2, 4, 5, 6), OrderNHWC)
    v3, = op(v1, v2)

    assert v3.axis_order == OrderNCHW
    assert v3.shape == [2, 9, 4, 5]


@raises(AssertionError)
def test_call_invalid_size():
    op = Concat("op", {"axis": Axis.C})

    v1 = Variable((2, 3, 4, 5), OrderNHWC)
    v2 = Variable((2, 3, 7, 6), OrderNHWC)
    v3, = op(v1, v2)
