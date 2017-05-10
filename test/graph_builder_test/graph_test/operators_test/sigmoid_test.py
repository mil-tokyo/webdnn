from graph_transpiler.graph.operators.sigmoid import Sigmoid
from test.util import template_elementwise_operator


def test_every_order():
    template_elementwise_operator(Sigmoid)
