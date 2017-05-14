from graph_transpiler.graph.axis import Axis
from graph_transpiler.graph.variables.attributes.order import Order, OrderNC


def test_compare_preset_order():
    assert OrderNC == OrderNC


def test_compare_custom_order():
    order1 = Order([Axis.N, Axis.C])

    assert OrderNC == order1
