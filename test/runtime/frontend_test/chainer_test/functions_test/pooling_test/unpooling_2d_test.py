import chainer
import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn import Placeholder
from webdnn.frontend.chainer.converter import ChainerConverter
from webdnn.frontend.chainer.placeholder_variable import PlaceholderVariable


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


def test_with_placeholder():
    vx = chainer.Variable(np.random.rand(2, 16, 7, 7).astype(np.float32))
    vy = chainer.functions.unpooling_2d(vx, ksize=3, stride=2, pad=0)

    N = Placeholder(label="N")
    C = Placeholder(label="C")
    px = PlaceholderVariable([N, C, 7, 7])
    py = chainer.functions.unpooling_2d(px, ksize=3, stride=2, pad=0)

    graph = ChainerConverter().convert([px], [py])

    N.value = 2
    C.value = 16
    generate_kernel_test_case(
        description=f"[chainer] F.unpooling_2d with placeholder",
        graph=graph,
        backend=["webgpu", "webassembly"],
        inputs={graph.inputs[0]: vx.data},
        expected={graph.outputs[0]: vy.data},
    )
