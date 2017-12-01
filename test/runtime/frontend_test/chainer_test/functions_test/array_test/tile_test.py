import chainer
import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn.frontend.chainer.converter import ChainerConverter


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
