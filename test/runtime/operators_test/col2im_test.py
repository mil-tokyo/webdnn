import numpy as np
from chainer.utils.conv import col2im_cpu, get_deconv_outsize

from test.util import generate_kernel_test_case, wrap_template
from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.operators.col2im import Col2Im
from webdnn.graph.order import OrderNHWC, OrderNCHW, Order
from webdnn.graph.variable import Variable

col_chainer_order = Order([Axis.N, Axis.C, Axis.KH, Axis.KW, Axis.H, Axis.W])


@wrap_template
def template(col_shape=(2, 5, 3, 3, 3, 4), col_order=col_chainer_order, im_order=OrderNHWC,
             ksize=(3, 3), padding=(1, 1), stride=(1, 1),
             description: str = ""):
    col = Variable(col_shape, col_order)
    op = Col2Im(None, ksize, stride, padding)
    im, = op(col)
    im = im.change_order(im_order)

    vcol = np.random.rand(*(col.shape_dict[a] for a in col_chainer_order.axes)).astype(np.float32)
    h1 = get_deconv_outsize(col.shape_dict[Axis.H], op.KH, op.SH, op.PH)
    w1 = get_deconv_outsize(col.shape_dict[Axis.W], op.KW, op.SW, op.PW)
    vim = col2im_cpu(vcol, op.SH, op.SW, op.PH, op.PW, h1, w1)

    vcol = vcol.transpose([col_chainer_order.axes_dict[a] for a in col_order.axes])
    vim = vim.transpose([OrderNCHW.axes_dict[a] for a in im_order.axes])

    generate_kernel_test_case(
        description=f"Col2Im {description}",
        backend=["webgpu", "webgl", "webassembly"],
        graph=Graph([col], [im]),
        inputs={col: vcol},
        expected={im: vim},
    )


def test_NHWC():
    template()


def test_NCHW():
    template(col_order=Order([Axis.N, Axis.C, Axis.KH, Axis.KW, Axis.H, Axis.W]), col_shape=(2, 5, 3, 3, 3, 4))


def test_wide_stride():
    template(ksize=3, stride=2, padding=1)


def test_no_padding():
    template(padding=0)
