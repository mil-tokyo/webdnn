from graph_builder.graph.axis import Axis
from graph_builder.graph.operator import Operator
from graph_builder.graph.variable import Variable
from graph_builder.graph.variables.attributes.order import OrderNHWC, OrderHWCN


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


def test_change_axis_order():
    v1 = Variable([1, 2, 3, 4], OrderNHWC)
    v1.change_axis_order(OrderHWCN)

    assert v1.ndim == 4
    assert v1.shape == [2, 3, 4, 1]
    assert len(v1.shape_dict) == 4
    assert v1.shape_dict[Axis.N] == 1
    assert v1.shape_dict[Axis.H] == 2
    assert v1.shape_dict[Axis.W] == 3
    assert v1.shape_dict[Axis.C] == 4


def test_merge():
    op1 = Operator("op")
    v1_1 = Variable([1, 2, 3, 4], OrderNHWC)
    v1_2 = Variable([1, 2, 3, 4], OrderNHWC)
    op2 = Operator("op")

    op1.append_output("v", v1_1)
    op2.append_input("v", v1_2)

    v1_1.merge(v1_2)

    assert v1_1.output_from == op1
    assert v1_1.input_to == {op2}
    assert v1_2.output_from is None
    assert v1_2.input_to == set()
