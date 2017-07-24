from test.webdnn_test.graph_test.operators_test.util import template_test_unary_operator
from webdnn.graph.operators.elu import Elu


def template():
    template_test_unary_operator(Elu)


def test():
    template()
