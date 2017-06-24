from test.util import template_elementwise_operator
from webdnn.graph.operators.clipped_relu import ClippedRelu


def test_every_order():
    template_elementwise_operator(ClippedRelu, {"cap": 10.0})
