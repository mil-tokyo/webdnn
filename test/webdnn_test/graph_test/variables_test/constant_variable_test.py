import numpy as np
from nose.tools import raises

from webdnn.graph.order import OrderNHWC, OrderHWNC, OrderNC, OrderCHWN, OrderCN
from webdnn.graph.variables.constant_variable import ConstantVariable


def test_change_order():
    d1 = np.arange(2 * 3 * 4 * 5).reshape((2, 3, 4, 5))

    v = ConstantVariable(d1, OrderNHWC)
    v.change_order(OrderHWNC)

    d2 = np.rollaxis(d1, 0, 3)

    assert v.order == OrderHWNC
    assert np.all(v.data == d2)


def test_change_order_with_expansion():
    d1 = np.arange(3 * 4).reshape((3, 4))
    v = ConstantVariable(d1, OrderNC)
    v.change_order(OrderCHWN)
    d2 = np.rollaxis(d1, 0, 2)

    assert v.order == OrderCHWN
    assert np.all(v.data.flatten() == d2.flatten())


def test_change_order_with_compression():
    d1 = np.arange(3 * 4).reshape((3, 1, 1, 4))
    v = ConstantVariable(d1, OrderNHWC)
    v.change_order(OrderCN)
    d2 = np.rollaxis(d1, 0, 4)

    assert v.order == OrderCN
    assert np.all(v.data.flatten() == d2.flatten())


@raises(AssertionError)
def test_change_order_with_invalid_compression():
    d1 = np.arange(3 * 2 * 2 * 4).reshape((3, 2, 2, 4))
    v = ConstantVariable(d1, OrderNHWC)
    v.change_order(OrderCN)
