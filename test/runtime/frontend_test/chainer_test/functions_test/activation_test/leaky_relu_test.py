import chainer
import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn import Placeholder
from webdnn.frontend.chainer.converter import ChainerConverter
from webdnn.frontend.chainer.placeholder_variable import PlaceholderVariable


@wrap_template
def template(x_shape=(2, 5, 6, 8), slope=0.5, description: str = ""):
    vx = chainer.Variable(np.random.rand(*x_shape).astype(np.float32))
    vy = chainer.functions.leaky_relu(vx, slope)

    graph = ChainerConverter().convert([vx], [vy])

    generate_kernel_test_case(
        description=f"[chainer] F.leaky_relu {description}",
        graph=graph,
        inputs={graph.inputs[0]: vx.data},
        expected={graph.outputs[0]: vy.data},
    )


def test():
    template()


def test_no_slope():
    template(slope=0)


def test_with_placeholder():
    vx = chainer.Variable(np.random.rand(10, 11, 12).astype(np.float32))
    vy = chainer.functions.leaky_relu(vx, slope=0.5)

    A = Placeholder(label="A")
    B = Placeholder(label="B")
    C = Placeholder(label="C")
    px = PlaceholderVariable([A, B, C])
    py = chainer.functions.leaky_relu(px, slope=0.5)

    graph = ChainerConverter().convert([px], [py])

    A.value = 10
    B.value = 11
    C.value = 12
    generate_kernel_test_case(
        description=f"[chainer] F.leaky_relu with placeholder",
        graph=graph,
        backend=["webgpu", "webassembly"],
        inputs={graph.inputs[0]: vx.data},
        expected={graph.outputs[0]: vy.data},
    )
