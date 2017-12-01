import chainer
import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn.frontend.chainer.converter import ChainerConverter


@wrap_template
def template(x_shape, axis, description: str = ""):
    vx = chainer.Variable(np.random.rand(*x_shape).astype(np.float32))
    vy = chainer.functions.expand_dims(vx, axis=axis)

    graph = ChainerConverter().convert([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    assert list(vy.shape) == list(y.shape), f"{vy.shape}, {y.shape}"
    generate_kernel_test_case(
        description=f"[chainer] F.expand_dims {description}",
        graph=graph,
        inputs={x: vx.data},
        expected={y: vy.data},
    )


def test_outer_side():
    template(x_shape=[3, 5], axis=0)


def test_middle():
    template(x_shape=[3, 5], axis=1)


def test_inner_side():
    template(x_shape=[3, 5], axis=2)


def test_negative_index():
    template(x_shape=[3, 5], axis=-2)
