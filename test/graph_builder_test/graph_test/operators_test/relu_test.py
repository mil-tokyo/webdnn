from graph_builder.graph.operators.relu import Relu

from test.util import test_elementwise_operator


def test_every_order():
    test_elementwise_operator(Relu)
