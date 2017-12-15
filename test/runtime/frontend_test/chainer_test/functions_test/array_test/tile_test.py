import chainer
import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn import Placeholder
from webdnn.frontend.chainer.converter import ChainerConverter
from webdnn.frontend.chainer.placeholder_variable import PlaceholderVariable


@wrap_template
def template(x_shape, reps, description=""):
    vx = chainer.Variable(np.random.rand(*x_shape).astype(np.float32))
    vy = chainer.functions.tile(vx, reps=reps)

    graph = ChainerConverter().convert([vx], [vy])

    assert list(graph.outputs[0].shape) == list(vy.shape)
    generate_kernel_test_case(
        description=f"[chainer] F.tile {description}",
        graph=graph,
        backend=["webgpu", "webassembly", "webgl"],
        inputs={graph.inputs[0]: vx.data},
        expected={graph.outputs[0]: vy.data},
    )


def test_int():
    template(x_shape=[3, 4, 5, 6], reps=2)


def test_short_reps():
    template(x_shape=[3, 4, 5, 6], reps=(2, 3))


def test_long_reps():
    template(x_shape=[3, 5], reps=(2, 3, 4, 5))


def test_with_placeholder():
    vx = chainer.Variable(np.random.rand(2, 5, 4, 8).astype(np.float32))
    vy = chainer.functions.tile(vx, reps=(1, 3, 4, 2))

    N = Placeholder(label="N")
    C = Placeholder(label="C")
    H = Placeholder(label="H")
    W = Placeholder(label="W")
    px = PlaceholderVariable([N, C, H, W])
    py = chainer.functions.tile(px, reps=(1, 3, 4, 2))

    graph = ChainerConverter().convert([px], [py])

    N.value = 2
    C.value = 5
    H.value = 4
    W.value = 8
    generate_kernel_test_case(
        description=f"[chainer] F.tile with placeholder",
        graph=graph,
        backend=["webgpu", "webassembly"],
        inputs={graph.inputs[0]: vx.data},
        expected={graph.outputs[0]: vy.data},
    )
