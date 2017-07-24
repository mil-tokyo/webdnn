from test.webdnn_test.graph_test.operators_test.util import template_test_unary_operator
from webdnn.graph.operators.hard_sigmoid import HardSigmoid


def template():
    template_test_unary_operator(HardSigmoid)


def test():
    template()
