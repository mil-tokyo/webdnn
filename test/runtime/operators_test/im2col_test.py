import numpy as np
from chainer.utils.conv import im2col_cpu

from test.util import generate_kernel_test_case, wrap_template
from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.operators.im2col import Im2Col
from webdnn.graph.order import OrderNHWC, OrderNCHW, OrderCNHW, Order
from webdnn.graph.variable import Variable

col_chainer_order = Order([Axis.N, Axis.C, Axis.KH, Axis.KW, Axis.H, Axis.W])


@wrap_template
def template(im_shape=[2, 3, 4, 5], im_order=OrderNCHW, col_order=col_chainer_order, ksize=(3, 3), padding=(1, 1), stride=(1, 1),
             dilation=(1, 1), description: str = ""):
    im = Variable(im_shape, im_order)
    op = Im2Col(None, ksize, stride, padding, dilation_rate=dilation)
    col, = op(im)
    col = col.change_order(col_order)

    vim = np.random.rand(*(im.shape_dict[a] for a in OrderNCHW.axes)).astype(np.float32)
    vcol = im2col_cpu(vim, op.KH, op.KW, op.SH, op.SW, op.PH, op.PW, dy=op.DH, dx=op.DW)

    vcol = vcol.transpose([col_chainer_order.axes_dict[a] for a in col_order.axes])
    vim = vim.transpose([OrderNCHW.axes_dict[a] for a in im_order.axes])

    generate_kernel_test_case(
        description=f"Im2Col {description}",
        backend=["webgpu", "webgl", "webassembly"],
        graph=Graph([im], [col]),
        inputs={im: vim},
        expected={col: vcol},
    )


def test_NCHW():
    template()


def test_NHWC():
    template(im_order=OrderNHWC)


def test_CNHW():
    template(im_order=OrderCNHW)


def test_wide_stride():
    template(ksize=3, stride=2, padding=1)


def test_dilated():
    template(ksize=3, stride=1, padding=1, dilation=2, im_order=OrderNHWC, im_shape=[1, 3, 5, 2])
