import chainer
import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn.frontend.chainer.converter import ChainerConverter


@wrap_template
def template(ksize=3, stride=1, pad=0, dilate=1, nobias=True, description=""):
    link = chainer.links.DilatedConvolution2D(4, 10, ksize=ksize, stride=stride, pad=pad, dilate=dilate, nobias=nobias)
    vx = chainer.Variable(np.random.rand(2, 4, 6, 11).astype(np.float32))
    vy = link(vx)

    graph = ChainerConverter().convert([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] L.DilatedConvolution2D {description}",
        graph=graph,
        backend=["webgpu", "webassembly"],
        inputs={x: vx.data},
        expected={y: vy.data},
        EPS=1e-2
    )


def test():
    template()


def test_dilate_2():
    template(dilate=2)


def test_nobias():
    template(nobias=True)


def test_irregular_kernel_size():
    template(ksize=(3, 4))


def test_irregular_stride_size():
    template(stride=(2, 3))


def test_irregular_padding_size():
    template(pad=(1, 2))


def test_irregular_size():
    template(ksize=(3, 5), stride=(2, 3), pad=(1, 3))
