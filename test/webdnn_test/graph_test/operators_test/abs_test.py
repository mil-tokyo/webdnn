from test.webdnn_test.graph_test.operators_test.util import template_test_unary_operator
from webdnn.graph.operators.abs import Abs


def template():
    template_test_unary_operator(Abs)


def test():
    template()
