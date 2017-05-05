from graph_builder.graph.operators.tanh import Tanh

from test.util import test_elementwise_operator


def test_every_order():
    test_elementwise_operator(Tanh)
