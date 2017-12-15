import chainer
import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn import Placeholder
from webdnn.frontend.chainer.converter import ChainerConverter
from webdnn.frontend.chainer.placeholder_variable import PlaceholderVariable


@wrap_template
def template(ksize=2, stride=None, pad=0, shape=(2, 4, 6, 8), description=""):
    vx = chainer.Variable(np.random.rand(*shape).astype(np.float32))
    vy = chainer.functions.average_pooling_2d(vx, ksize=ksize, stride=stride, pad=pad)

    graph = ChainerConverter().convert([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] F.average_pooling_2d {description}",
        graph=graph,
        inputs={x: vx.data},
        expected={y: vy.data},
    )


def test():
    template()


def test_padding_not_zero():
    template(pad=1)


# TODO: chainer's average pooling does not support cover_all=True mode
# def test_odd_size_and_cover_all():
#     template(shape=(2, 4, 5, 7), stride=2)


def test_stride_is_none():
    template(stride=None, pad=1)


def test_irregular_size():
    template(ksize=(3, 4), stride=(1, 2), pad=(1, 3))


def test_with_placeholder():
    vx = chainer.Variable(np.random.rand(2, 16, 7, 7).astype(np.float32))
    vy = chainer.functions.average_pooling_2d(vx, ksize=3, stride=2, pad=0)

    H = Placeholder(label="H")
    W = Placeholder(label="W")
    px = PlaceholderVariable([2, 16, H, W])
    py = chainer.functions.average_pooling_2d(px, ksize=3, stride=2, pad=0)

    graph = ChainerConverter().convert([px], [py])

    H.value = 7
    W.value = 7
    generate_kernel_test_case(
        description=f"[chainer] F.average_pooling_2d with placeholder",
        graph=graph,
        backend=["webgpu", "webassembly"],
        inputs={graph.inputs[0]: vx.data},
        expected={graph.outputs[0]: vy.data},
    )
