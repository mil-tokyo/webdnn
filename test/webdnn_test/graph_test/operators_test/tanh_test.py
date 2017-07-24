from test.webdnn_test.graph_test.operators_test.util import template_test_unary_operator
from webdnn.graph.operators.tanh import Tanh


def template():
    template_test_unary_operator(Tanh)


def test():
    template()
