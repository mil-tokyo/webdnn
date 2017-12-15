import chainer
import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn import Placeholder
from webdnn.frontend.chainer.converter import ChainerConverter
from webdnn.frontend.chainer.placeholder_variable import PlaceholderVariable


@wrap_template
def template(description: str = ""):
    vx0 = chainer.Variable(np.random.rand(2, 5, 6, 8).astype(np.float32))
    vx1 = chainer.Variable(np.random.rand(2, 5, 6, 8).astype(np.float32))
    vy = chainer.functions.minimum(vx0, vx1)

    graph = ChainerConverter().convert([vx0, vx1], [vy])

    x0 = graph.inputs[0]
    x1 = graph.inputs[1]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] F.minimum {description}",
        graph=graph,
        inputs={x0: vx0.data, x1: vx1.data},
        expected={y: vy.data},
    )


def test():
    template()


def test_with_placeholder():
    vx0 = chainer.Variable(np.random.rand(10, 11, 12).astype(np.float32))
    vx1 = chainer.Variable(np.random.rand(10, 11, 12).astype(np.float32))
    vy = chainer.functions.minimum(vx0, vx1)

    A = Placeholder(label="A")
    B = Placeholder(label="B")
    C = Placeholder(label="C")
    px0 = PlaceholderVariable([A, B, C])
    px1 = PlaceholderVariable([A, B, C])
    py = chainer.functions.minimum(px0, px1)

    graph = ChainerConverter().convert([px0, px1], [py])

    A.value = 10
    B.value = 11
    C.value = 12
    generate_kernel_test_case(
        description=f"[chainer] F.minimum with placeholder",
        graph=graph,
        backend=["webgpu", "webassembly"],
        inputs={graph.inputs[0]: vx0.data, graph.inputs[1]: vx1.data},
        expected={graph.outputs[0]: vy.data},
    )
