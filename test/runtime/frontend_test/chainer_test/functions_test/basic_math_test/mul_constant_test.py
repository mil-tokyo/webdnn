import chainer
import numpy as np

from test.util import generate_kernel_test_case
from webdnn import Placeholder
from webdnn.frontend.chainer.converter import ChainerConverter
from webdnn.frontend.chainer.placeholder_variable import PlaceholderVariable


def template(vx, vy, description: str = ""):
    graph = ChainerConverter().convert([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] F.MulConstant {description}",
        graph=graph,
        inputs={x: vx.data},
        expected={y: vy.data},
    )


def test_mul():
    vx = chainer.Variable(np.random.rand(2, 4, 6, 8).astype(np.float32))
    vy = vx * 2
    template(vx, vy, "lhs")


def test_rmul():
    vx = chainer.Variable(np.random.rand(2, 4, 6, 8))
    vy = 2 * vx
    template(vx, vy, "rhs")


def test_with_placeholder():
    vx = chainer.Variable(np.random.rand(1, 3, 16, 16).astype(np.float32))
    vy = vx * 2  # type: chainer.Variable

    H = Placeholder(label="H")
    W = Placeholder(label="W")
    px = PlaceholderVariable([1, 3, H, W])
    py = px * 2  # type: chainer.Variable

    graph = ChainerConverter().convert([px], [py])

    x = graph.inputs[0]
    y = graph.outputs[0]

    H.value = 16
    W.value = 16
    generate_kernel_test_case(
        description=f"[chainer] F.MulConstant with placeholder",
        graph=graph,
        backend=["webgpu", "webassembly"],
        inputs={x: vx.data},
        expected={y: vy.data}
    )
