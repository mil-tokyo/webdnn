from test.webdnn_test.graph_test.operators_test.util import template_test_unary_operator
from webdnn.graph.operators.relu import Relu


def template():
    template_test_unary_operator(Relu)


def test():
    template()
