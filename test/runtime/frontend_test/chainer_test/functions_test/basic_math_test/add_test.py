import chainer
import numpy as np

from test.util import generate_kernel_test_case
from webdnn import Placeholder
from webdnn.frontend.chainer.converter import ChainerConverter
from webdnn.frontend.chainer.placeholder_variable import PlaceholderVariable


def test():
    vx1 = chainer.Variable(np.random.rand(2, 4, 6, 8).astype(np.float32))
    vx2 = chainer.Variable(np.random.rand(2, 4, 6, 8).astype(np.float32))
    vy = vx1 + vx2

    graph = ChainerConverter().convert([vx1, vx2], [vy])

    x1 = graph.inputs[0]
    x2 = graph.inputs[1]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] F.Add",
        graph=graph,
        inputs={
            x1: vx1.data,
            x2: vx2.data
        },
        expected={y: vy.data},
    )


def test_itself():
    vx = chainer.Variable(np.random.rand(2, 4, 6, 8))
    vy = vx + vx

    graph = ChainerConverter().convert([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] F.Add itself",
        graph=graph,
        inputs={x: vx.data},
        expected={y: vy.data},
    )


def test_with_placeholder():
    vx1 = chainer.Variable(np.random.rand(1, 3, 16, 16).astype(np.float32))
    vx2 = chainer.Variable(np.random.rand(1, 3, 16, 16).astype(np.float32))
    vy = vx1 + vx2

    H = Placeholder(label="H")
    W = Placeholder(label="W")
    px1 = PlaceholderVariable([1, 3, H, W])
    px2 = PlaceholderVariable([1, 3, H, W])
    py = px1 + px2

    graph = ChainerConverter().convert([px1, px2], [py])

    H.value = 16
    W.value = 16
    generate_kernel_test_case(
        description=f"[chainer] F.Add with placeholder",
        graph=graph,
        backend=["webgpu", "webassembly"],
        inputs={graph.inputs[0]: vx1.data, graph.inputs[1]: vx2.data},
        expected={graph.outputs[0]: vy.data}
    )
