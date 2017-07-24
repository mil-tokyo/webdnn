from test.webdnn_test.graph_test.operators_test.util import template_test_unary_operator
from webdnn.graph.operators.scalar_add import ScalarAdd


def template():
    template_test_unary_operator(ScalarAdd, {"value": 2})


def test():
    template()
