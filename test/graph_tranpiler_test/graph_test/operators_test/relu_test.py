from graph_transpiler.graph.operators.relu import Relu

from test.util import template_elementwise_operator


def test_every_order():
    template_elementwise_operator(Relu)
