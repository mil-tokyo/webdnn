from graph_builder.graph.operators.tanh import Tanh

from test.util import template_elementwise_operator


def test_every_order():
    template_elementwise_operator(Tanh)
