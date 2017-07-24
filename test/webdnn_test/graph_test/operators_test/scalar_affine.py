from test.webdnn_test.graph_test.operators_test.util import template_test_unary_operator
from webdnn.graph.operators.scalar_affine import ScalarAffine


def template():
    template_test_unary_operator(ScalarAffine, {"scale": 2.0, "bias": 3.0})


def test():
    template()
