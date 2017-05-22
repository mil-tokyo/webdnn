from test.util import template_elementwise_operator
from webdnn.graph.operators.sigmoid import Sigmoid


def test_every_order():
    template_elementwise_operator(Sigmoid)
