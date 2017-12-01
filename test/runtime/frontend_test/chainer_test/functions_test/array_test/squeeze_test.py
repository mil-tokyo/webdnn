import chainer
import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn.frontend.chainer.converter import ChainerConverter


@wrap_template
def template(x_shape, axis, description=""):
    vx = chainer.Variable(np.random.rand(*x_shape).astype(np.float32))
    vy = chainer.functions.squeeze(vx, axis=axis)

    graph = ChainerConverter().convert([vx], [vy])

    assert list(graph.outputs[0].shape) == list(vy.shape)
    generate_kernel_test_case(
        description=f"[chainer] F.squeeze {description}",
        graph=graph,
        inputs={graph.inputs[0]: vx.data},
        expected={graph.outputs[0]: vy.data},
    )


def test_int():
    template(x_shape=[3, 4, 1, 6], axis=2)


def test_int_keep_others():
    template(x_shape=[3, 1, 5, 1, 6, 1], axis=3)


def test_tuple():
    template(x_shape=[1, 4, 1, 6], axis=(0, 2))


def test_none():
    template(x_shape=[1, 1, 5, 1], axis=None)
