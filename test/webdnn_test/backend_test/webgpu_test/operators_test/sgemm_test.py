from nose.tools import raises

from webdnn.backend.webgpu.operators.sgemm import Sgemm
from webdnn.graph.axis import Axis
from webdnn.graph.order import OrderNHWC, OrderNC
from webdnn.graph.variable import Variable


def test_sgemm():
    op = Sgemm(None, M=10, N=20, K=30, out_shape=[1, 10, 4, 5], out_order=OrderNHWC, transpose_A=True, transpose_B=True)

    x = Variable((10, 30), OrderNC)
    w = Variable((20, 30), OrderNC)

    y, = op(x, w)

    assert y.order == OrderNHWC
    assert y.shape_dict[Axis.N] == 1
    assert y.shape_dict[Axis.H] == 10
    assert y.shape_dict[Axis.W] == 4
    assert y.shape_dict[Axis.C] == 5


@raises(AssertionError)
def test_sgemm_invalid_A_shape():
    op = Sgemm(None, M=10, N=20, K=30, out_shape=[1, 10, 4, 5], out_order=OrderNHWC, transpose_A=True, transpose_B=True)

    x = Variable((20, 30), OrderNC)
    w = Variable((20, 30), OrderNC)
    op(x, w)


@raises(AssertionError)
def test_sgemm_invalid_B_shape():
    op = Sgemm(None, M=10, N=20, K=30, out_shape=[1, 10, 4, 5], out_order=OrderNHWC, transpose_A=True, transpose_B=True)

    x = Variable((10, 30), OrderNC)
    w = Variable((10, 30), OrderNC)
    op(x, w)


@raises(AssertionError)
def test_sgemm_invalid_C_shape():
    op = Sgemm(None, M=10, N=20, K=30, out_shape=[1, 2, 3, 4], out_order=OrderNHWC, transpose_A=True, transpose_B=True)

    x = Variable((10, 30), OrderNC)
    w = Variable((20, 30), OrderNC)
    op(x, w)
