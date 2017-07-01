from test.util import template_elementwise_operator
from webdnn.graph.operators.scalar_affine import ScalarAffine


def test_every_order():
    template_elementwise_operator(ScalarAffine, operator_kwargs={"scale": 1, "bias": 0})
