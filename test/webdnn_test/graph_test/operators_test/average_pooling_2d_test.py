from test.webdnn_test.graph_test.operators_test.util import template_test_unary_operator
from webdnn.graph.axis import Axis, AxisKeyDict
from webdnn.graph.operators.average_pooling_2d import AveragePooling2D


def template(ksize=3, stride=1, pad=1, height=2, width=3, expected_dict=None):
    template_test_unary_operator(AveragePooling2D, {"ksize": ksize, "stride": stride, "padding": pad},
                                 test1d=False, test2d=False, test3d=False, test4d=True,
                                 axes=[Axis.N, Axis.H, Axis.W, Axis.C],
                                 shape_dict=AxisKeyDict([Axis.N, Axis.H, Axis.W, Axis.C], [2, height, width, 4]),
                                 expected_dict=expected_dict)


def test():
    template(expected_dict=AxisKeyDict([Axis.N, Axis.H, Axis.W, Axis.C], [2, 2, 3, 4]))


def test_large_stride():
    template(stride=2,
             height=(2 - 1) * 2 + 3 - 2 * 1,
             width=(3 - 1) * 2 + 3 - 2 * 1,
             expected_dict=AxisKeyDict([Axis.N, Axis.H, Axis.W, Axis.C], [2, 2, 3, 4]))


def test_no_padding():
    template(pad=0,
             height=(2 - 1) * 1 + 3 - 2 * 0,
             width=(3 - 1) * 1 + 3 - 2 * 0,
             expected_dict=AxisKeyDict([Axis.N, Axis.H, Axis.W, Axis.C], [2, 2, 3, 4]))


def test_projection():
    template(ksize=1, stride=1, pad=0,
             height=(2 - 1) * 1 + 1 - 2 * 0,
             width=(3 - 1) * 1 + 1 - 2 * 0,
             expected_dict=AxisKeyDict([Axis.N, Axis.H, Axis.W, Axis.C], [2, 2, 3, 4]))


def test_global():
    template(ksize=(3, 4), stride=1, pad=0,
             height=3, width=4,
             expected_dict=AxisKeyDict([Axis.N, Axis.H, Axis.W, Axis.C], [2, 1, 1, 4]))
