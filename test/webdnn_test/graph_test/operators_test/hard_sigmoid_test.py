from test.util import template_elementwise_operator
from webdnn.graph.operators.hard_sigmoid import HardSigmoid


def test_every_order():
    template_elementwise_operator(HardSigmoid)
