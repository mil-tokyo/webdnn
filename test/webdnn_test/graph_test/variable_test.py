from nose.tools import raises

from webdnn.graph.axis import Axis
from webdnn.graph.order import OrderNHWC, OrderHWCN, OrderNC, OrderCHWN, OrderCN
from webdnn.graph.variable import Variable


def test_construction():
    v1 = Variable([1, 2, 3, 4], OrderNHWC)

    assert v1.shape == (1, 2, 3, 4)
    assert v1.order == OrderNHWC


def test_size():
    v1 = Variable([1, 2, 3, 4], OrderNHWC)

    assert v1.size == 1 * 2 * 3 * 4


def test_ndim():
    v1 = Variable([1, 2, 3, 4], OrderNHWC)

    assert v1.ndim == 4


def test_shape_dict():
    v1 = Variable([1, 2, 3, 4], OrderNHWC)

    assert len(v1.shape_dict) == 4
    assert v1.shape_dict[Axis.N] == 1
    assert v1.shape_dict[Axis.H] == 2
    assert v1.shape_dict[Axis.W] == 3
    assert v1.shape_dict[Axis.C] == 4


def test_change_order():
    v = Variable([1, 2, 3, 4], OrderNHWC)
    v.change_order(OrderHWCN)

    assert v.order == OrderHWCN
    assert v.shape == (2, 3, 4, 1)


def test_change_order_with_expansion():
    v = Variable([3, 4], OrderNC)
    v.change_order(OrderCHWN)

    assert v.order == OrderCHWN
    assert v.shape == (4, 1, 1, 3)


def test_change_order_with_compression():
    v = Variable([3, 1, 1, 4], OrderNHWC)
    v.change_order(OrderCN)

    assert v.order == OrderCN
    assert v.shape == (4, 3)


@raises(AssertionError)
def test_change_order_with_invalid_compression():
    v = Variable([3, 2, 2, 4], OrderNHWC)
    v.change_order(OrderCN)
