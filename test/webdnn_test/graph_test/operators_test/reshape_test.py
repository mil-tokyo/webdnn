from nose.tools import raises

from test.util import assert_shape
from webdnn import Variable, Axis
from webdnn.graph.operators.reshape import Reshape
from webdnn.graph.order import OrderNC, OrderNHWC


def template(in_order, in_shape, out_order, out_shape):
    op = Reshape(None, in_order=in_order, out_order=out_order, out_shape=[out_shape[a] for a in out_order.axes])
    x = Variable([in_shape[a] for a in in_order.axes], in_order)
    y, = op(x)
    assert_shape(y, out_shape)


def test():
    template(in_order=OrderNC, in_shape={Axis.N: 2, Axis.C: 3}, out_order=OrderNC, out_shape={Axis.N: 3, Axis.C: 2})


def test_add_new_axis():
    template(in_order=OrderNC, in_shape={Axis.N: 2, Axis.C: 3},
             out_order=OrderNHWC, out_shape={Axis.N: 3, Axis.H: 1, Axis.W: 1, Axis.C: 2})


def test_remove_axis():
    template(in_order=OrderNHWC, in_shape={Axis.N: 2, Axis.H: 1, Axis.W: 1, Axis.C: 3},
             out_order=OrderNC, out_shape={Axis.N: 3, Axis.C: 2})


@raises(AssertionError)
def test_size_change():
    template(in_order=OrderNHWC, in_shape={Axis.N: 3, Axis.H: 1, Axis.W: 1, Axis.C: 3},
             out_order=OrderNC, out_shape={Axis.N: 3, Axis.C: 2})
