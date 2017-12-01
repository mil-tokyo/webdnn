import chainer
import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn.frontend.chainer.converter import ChainerConverter


@wrap_template
def template(axis, keepdims, description: str = ""):
    vx = chainer.Variable(np.random.rand(2, 5, 6, 8).astype(np.float32))
    vy = chainer.functions.max(vx, axis=axis, keepdims=keepdims)

    graph = ChainerConverter().convert([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    assert list(vy.shape) == list(y.shape), f"{vy.shape}, {y.shape}"
    generate_kernel_test_case(
        description=f"[chainer] F.max {description}",
        graph=graph,
        backend=["webgpu", "webgl", "webassembly"],
        inputs={x: vx.data},
        expected={y: vy.data},
    )


def test_axis_tuple():
    template(axis=(1, 3), keepdims=True)


def test_axis_int():
    template(axis=1, keepdims=True)


def test_axis_none():
    template(axis=None, keepdims=True)


def test_no_keepdims():
    template(axis=(1, 3), keepdims=False)
