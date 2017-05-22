from test.util import template_elementwise_operator
from webdnn.graph.operators.tanh import Tanh


def test_every_order():
    template_elementwise_operator(Tanh)
