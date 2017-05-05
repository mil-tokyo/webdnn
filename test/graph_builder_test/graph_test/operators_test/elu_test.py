from graph_builder.graph.operators.elu import Elu

from test.util import test_elementwise_operator


def test_every_order():
    test_elementwise_operator(Elu)
