import numpy as np

from graph_transpiler.graph.variables.attributes.order import OrderNHWC, OrderHWNC
from graph_transpiler.graph.variables.constant_variable import ConstantVariable


def test_change_order():
    d1 = np.arange(2 * 3 * 4 * 5).reshape((2, 3, 4, 5))

    v1 = ConstantVariable(d1, OrderNHWC)
    v1.change_order(OrderHWNC)

    d2 = np.rollaxis(d1, 0, 3)

    assert np.all(v1.data == d2)
