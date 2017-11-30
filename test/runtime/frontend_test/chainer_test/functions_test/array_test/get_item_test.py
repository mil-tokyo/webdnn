import chainer
import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn.frontend.chainer.converter import ChainerConverter


@wrap_template
def template(vx, vy, description: str = ""):
    graph = ChainerConverter().convert([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    assert list(vy.shape) == list(y.shape), f"vy_shape: {vy.shape}, y.shape: {y.shape}"

    generate_kernel_test_case(
        description=f"[chainer] F.get_item {description}",
        graph=graph,
        backend=["webgpu", "webgl", "webassembly"],
        inputs={x: vx.data},
        expected={y: vy.data}
    )


def test():
    x = chainer.Variable(np.random.rand(5, 6, 7, 8).astype(np.float32))
    y = x[2:5, 2:5, 2:5, 2:5]
    template(x, y)


def test_no_slice():
    x = chainer.Variable(np.random.rand(5, 6, 7, 8).astype(np.float32))
    y = x[:, :, :, :]
    template(x, y)


def test_remove_axis():
    x = chainer.Variable(np.random.rand(5, 6, 7, 8).astype(np.float32))
    y = x[:, 5, 3, :]
    template(x, y)


def test_insert_axis():
    x = chainer.Variable(np.random.rand(5, 6, 7, 8).astype(np.float32))
    y = x[:, :, None, :, :]
    template(x, y)


def test_large_step():
    x = chainer.Variable(np.random.rand(5, 6, 7, 8).astype(np.float32))
    y = x[::2, ::3, 1::4, 2::5]
    template(x, y)


def test_explicit_ellipsis():
    x = chainer.Variable(np.random.rand(5, 6, 7, 8).astype(np.float32))
    y = x[2:5, ..., 2:5]
    template(x, y)


def test_implicit_ellipsis():
    x = chainer.Variable(np.random.rand(5, 6, 7, 8).astype(np.float32))
    y = x[2:5]
    template(x, y)
