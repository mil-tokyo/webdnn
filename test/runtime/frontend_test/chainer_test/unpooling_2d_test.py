import chainer
import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn.frontend.chainer.converter import ChainerConverter


@wrap_template
def template(ksize=2, stride=None, pad=0, cover_all=True, shape=(2, 4, 6, 8), description=""):
    vx = chainer.Variable(np.random.rand(*shape).astype(np.float32))
    vy = chainer.functions.unpooling_2d(vx, ksize=ksize, stride=stride, pad=pad, cover_all=cover_all)

    graph = ChainerConverter().convert([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] F.unpooling_2d {description}",
        graph=graph,
        backend=["webgpu", "webgl", "webassembly"],
        inputs={x: vx.data},
        expected={y: vy.data},
    )


def test():
    template()


def test_padding_not_zero():
    template(pad=1)


def test_stride_is_none():
    template(stride=None, pad=1)


def test_cover_all_false():
    template(stride=2, cover_all=False)


def test_irregular_size():
    template(ksize=(3, 4), stride=(1, 2), pad=(1, 3))
