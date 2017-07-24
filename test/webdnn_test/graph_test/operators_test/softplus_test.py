from test.webdnn_test.graph_test.operators_test.util import template_test_unary_operator
from webdnn.graph.operators.softplus import Softplus


def template():
    template_test_unary_operator(Softplus, {"beta": 1.0})


def test():
    template()
