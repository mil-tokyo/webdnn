from test.webdnn_test.graph_test.operators_test.util import template_test_unary_operator
from webdnn.graph.operators.leaky_relu import LeakyRelu


def template():
    template_test_unary_operator(LeakyRelu, {"slope": 0.3})


def test():
    template()
