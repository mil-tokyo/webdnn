from graph_builder.graph.operators.sigmoid import Sigmoid
from test.util import test_elementwise_operator


def test_every_order():
    test_elementwise_operator(Sigmoid)
