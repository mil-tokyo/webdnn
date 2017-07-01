from test.util import template_elementwise_operator
from webdnn.graph.operators.softplus import Softplus


def test_every_order():
    template_elementwise_operator(Softplus, {"beta": 1.0})
