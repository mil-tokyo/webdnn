from test.webdnn_test.graph_test.operators_test.util import template_test_unary_operator
from webdnn.graph.axis import Axis
from webdnn.graph.operators.local_response_normalization import LocalResponseNormalization


def template():
    template_test_unary_operator(LocalResponseNormalization, {"n": 1, "k": 2, "alpha": 0.1, "beta": 0.2},
                                 test1d=False, test2d=False, test3d=False, test4d=True,
                                 axes=[Axis.N, Axis.H, Axis.W, Axis.C])


def test():
    template()
