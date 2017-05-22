from test.util import template_elementwise_operator
from webdnn.graph.operators.relu import Relu


def test_every_order():
    template_elementwise_operator(Relu)
