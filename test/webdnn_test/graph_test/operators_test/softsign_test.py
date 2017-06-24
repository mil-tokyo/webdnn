from test.util import template_elementwise_operator
from webdnn.graph.operators.softsign import Softsign


def test_every_order():
    template_elementwise_operator(Softsign)
