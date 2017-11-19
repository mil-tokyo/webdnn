import chainer
import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn.frontend.chainer.converter import ChainerConverter


@wrap_template
def template(N=2, H=14, W=15, C1=16, C2=17, ksize=3, stride=1, pad=1, nobias=True, description=""):
    link = chainer.links.Deconvolution2D(C1, C2, ksize=ksize, stride=stride, pad=pad, nobias=nobias)
    vx = chainer.Variable(np.arange(np.product([N, C1, H, W])).reshape(N, C1, H, W).astype(np.float32))
    vy = link(vx)

    graph = ChainerConverter().convert([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] L.Deconvolution2D {description}",
        graph=graph,
        backend=["webgpu", "webgl", "webassembly"],
        inputs={x: vx.data},
        expected={y: vy.data},
        EPS=1e-2
    )


def test():
    template()


def test_no_padding():
    template(pad=0)


def test_no_bias():
    template(nobias=True)


def test_irregular_kernel_size():
    template(ksize=(3, 4))


def test_irregular_stride_size():
    template(stride=(2, 3))


def test_irregular_padding_size():
    template(pad=(1, 2))


def test_irregular_size():
    template(ksize=(3, 5), stride=(2, 3), pad=(1, 3))
