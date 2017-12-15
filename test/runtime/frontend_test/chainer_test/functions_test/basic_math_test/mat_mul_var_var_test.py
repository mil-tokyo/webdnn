import chainer
import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn import Placeholder
from webdnn.frontend.chainer.converter import ChainerConverter
from webdnn.frontend.chainer.placeholder_variable import PlaceholderVariable


@wrap_template
def template(a_shape=(2, 4), b_shape=(4, 6), description: str = ""):
    vx1 = chainer.Variable(np.random.rand(*a_shape).astype(np.float32))
    vx2 = chainer.Variable(np.random.rand(*b_shape).astype(np.float32))
    vy = vx1 @ vx2

    graph = ChainerConverter().convert([vx1, vx2], [vy])

    x1 = graph.inputs[0]
    x2 = graph.inputs[1]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] F.MatMulVarVar {description}",
        graph=graph,
        inputs={
            x1: vx1.data,
            x2: vx2.data
        },
        expected={y: vy.data},
    )


def test():
    template()


def test_itself():
    vx = chainer.Variable(np.random.rand(8, 8))
    vy = vx @ vx

    graph = ChainerConverter().convert([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] F.MatMulVarVar itself",
        graph=graph,
        inputs={x: vx.data},
        expected={y: vy.data},
    )


def test_with_placeholder():
    vx1 = chainer.Variable(np.random.rand(2, 8).astype(np.float32))
    vx2 = chainer.Variable(np.random.rand(8, 6).astype(np.float32))
    vy = vx1 @ vx2

    M = Placeholder(label="M")
    N = Placeholder(label="N")
    px1 = PlaceholderVariable([M, 8])
    px2 = PlaceholderVariable([8, N])
    py = px1 @ px2

    graph = ChainerConverter().convert([px1, px2], [py])

    M.value = 2
    N.value = 6
    generate_kernel_test_case(
        description=f"[chainer] F.MatMulVarVar with placeholder",
        graph=graph,
        backend=["webgpu", "webassembly"],
        inputs={graph.inputs[0]: vx1.data, graph.inputs[1]: vx2.data},
        expected={graph.outputs[0]: vy.data}
    )
