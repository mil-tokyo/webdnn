from nose.tools import raises

from test.util import assert_shape
from webdnn import Variable, Axis
from webdnn.graph.axis import AxisKeyDict
from webdnn.graph.operators.reinterpret_axis import ReinterpretAxis
from webdnn.graph.order import OrderNC, OrderNHWC, OrderNT


def template(in_order, in_shape, out_order, out_shape):
    op = ReinterpretAxis(None, in_order=in_order, out_order=out_order)
    x = Variable([in_shape[a] for a in in_order.axes], in_order)
    y, = op(x)
    assert_shape(y, out_shape)


def test():
    template(in_order=OrderNC, in_shape=AxisKeyDict([Axis.N, Axis.C], [2, 3]),
             out_order=OrderNT, out_shape=AxisKeyDict([Axis.N, Axis.T], [2, 3]))


@raises(AssertionError)
def test_ndim_change():
    template(in_order=OrderNHWC, in_shape=AxisKeyDict([Axis.N, Axis.H, Axis.W, Axis.C], [3, 1, 1, 3]),
             out_order=OrderNC, out_shape=AxisKeyDict([Axis.N, Axis.C], [3, 3]))
