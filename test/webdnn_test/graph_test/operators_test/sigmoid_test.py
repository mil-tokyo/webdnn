from test.webdnn_test.graph_test.operators_test.util import template_test_unary_operator
from webdnn.graph.operators.sigmoid import Sigmoid


def template():
    template_test_unary_operator(Sigmoid)


def test():
    template()
