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
        description=f"[chainer] F.MatMul{{Var, Constant}} {description}",
        graph=graph,
        inputs={x: vx.data},
        expected={y: vy.data},
    )


def test_mul():
    vx = chainer.Variable(np.random.rand(2, 8).astype(np.float32))
    vy = vx @ np.random.rand(8, 4)
    template(vx, vy, "lhs")


def test_rmul():
    vx = chainer.Variable(np.random.rand(2, 8))
    vy = np.random.rand(4, 2) @ vx
    template(vx, vy, "rhs")


def test_with_placeholder():
    rhs = np.random.rand(8, 4)

    vx = chainer.Variable(np.random.rand(2, 8).astype(np.float32))
    vy = vx @ rhs

    M = Placeholder(label="M")
    px = PlaceholderVariable([M, 8])
    py = px @ rhs

    graph = ChainerConverter().convert([px], [py])

    x = graph.inputs[0]
    y = graph.outputs[0]

    M.value = 2
    generate_kernel_test_case(
        description=f"[chainer] F.MatMulVarConstant with placeholder",
        graph=graph,
        backend=["webgpu", "webassembly"],
        inputs={x: vx.data},
        expected={y: vy.data},
    )
