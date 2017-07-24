from nose.tools import raises

from test.util import assert_shape
from webdnn import Variable, Axis
from webdnn.graph.operators.reinterpret_axis import ReinterpretAxis
from webdnn.graph.order import OrderNC, OrderNHWC, OrderNT


def template(in_order, in_shape, out_order, out_shape):
    op = ReinterpretAxis(None, in_order=in_order, out_order=out_order)
    x = Variable([in_shape[a] for a in in_order.axes], in_order)
    y, = op(x)
    assert_shape(y, out_shape)


def test():
    template(in_order=OrderNC, in_shape={Axis.N: 2, Axis.C: 3}, out_order=OrderNT, out_shape={Axis.N: 2, Axis.T: 3})


@raises(AssertionError)
def test_ndim_change():
    template(in_order=OrderNHWC, in_shape={Axis.N: 3, Axis.H: 1, Axis.W: 1, Axis.C: 3},
             out_order=OrderNC, out_shape={Axis.N: 3, Axis.C: 3})
