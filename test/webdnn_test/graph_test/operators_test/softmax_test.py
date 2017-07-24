from test.webdnn_test.graph_test.operators_test.util import template_test_unary_operator
from webdnn import Axis
from webdnn.graph.operators.softmax import Softmax


def template():
    template_test_unary_operator(Softmax, {"axis": Axis.C},
                                 test1d=False, test2d=True, test3d=False, test4d=False,
                                 axes=[Axis.N, Axis.C])
    template_test_unary_operator(Softmax, {"axis": Axis.C},
                                 test1d=False, test2d=False, test3d=True, test4d=False,
                                 axes=[Axis.N, Axis.C, Axis.T])
    template_test_unary_operator(Softmax, {"axis": Axis.C},
                                 test1d=False, test2d=False, test3d=False, test4d=True,
                                 axes=[Axis.N, Axis.C, Axis.H, Axis.W])


def test():
    template()
