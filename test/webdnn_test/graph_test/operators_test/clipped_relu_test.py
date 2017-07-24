from test.webdnn_test.graph_test.operators_test.util import template_test_unary_operator
from webdnn.graph.operators.clipped_relu import ClippedRelu


def template():
    template_test_unary_operator(ClippedRelu, {"cap": 10.0})


def test():
    template()
