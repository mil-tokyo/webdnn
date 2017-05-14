from graph_transpiler.graph.axis import Axis
from graph_transpiler.graph.operator import Operator
from graph_transpiler.graph.variable import Variable
from graph_transpiler.graph.variables.attributes.order import OrderNHWC, OrderHWCN


def test_construction():
    v1 = Variable([1, 2, 3, 4], OrderNHWC)

    assert v1.shape == [1, 2, 3, 4]
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
    v1 = Variable([1, 2, 3, 4], OrderNHWC)
    v1.change_order(OrderHWCN)

    assert v1.ndim == 4
    assert v1.shape == [2, 3, 4, 1]
    assert len(v1.shape_dict) == 4
    assert v1.shape_dict[Axis.N] == 1
    assert v1.shape_dict[Axis.H] == 2
    assert v1.shape_dict[Axis.W] == 3
    assert v1.shape_dict[Axis.C] == 4
