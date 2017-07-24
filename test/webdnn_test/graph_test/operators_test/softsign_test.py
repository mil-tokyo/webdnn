from test.webdnn_test.graph_test.operators_test.util import template_test_unary_operator
from webdnn.graph.operators.softsign import Softsign


def template():
    template_test_unary_operator(Softsign)


def test():
    template()
