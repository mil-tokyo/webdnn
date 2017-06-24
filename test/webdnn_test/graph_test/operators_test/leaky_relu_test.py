from test.util import template_elementwise_operator
from webdnn.graph.operators.leaky_relu import LeakyRelu


def test_every_order():
    template_elementwise_operator(LeakyRelu, {"slope": 0.5})
