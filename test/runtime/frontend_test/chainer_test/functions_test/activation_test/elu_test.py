import chainer
import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn import Placeholder
from webdnn.frontend.chainer.converter import ChainerConverter
from webdnn.frontend.chainer.placeholder_variable import PlaceholderVariable


@wrap_template
def template(alpha=1.0, description: str = ""):
    vx = chainer.Variable(np.random.rand(2, 5, 6, 8).astype(np.float32))
    vy = chainer.functions.elu(vx, alpha=alpha)

    graph = ChainerConverter().convert([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] F.elu {description}",
        graph=graph,
        inputs={x: vx.data},
        expected={y: vy.data},
    )


def test():
    template()


def test_alpha():
    template(alpha=0.5)


def test_alpha_0():
    template(alpha=0)


def test_with_placeholder():
    vx = chainer.Variable(np.random.rand(10, 11, 12).astype(np.float32))
    vy = chainer.functions.elu(vx, alpha=1.0)

    A = Placeholder(label="A")
    B = Placeholder(label="B")
    C = Placeholder(label="C")
    px = PlaceholderVariable([A, B, C])
    py = chainer.functions.elu(px, alpha=1.0)

    graph = ChainerConverter().convert([px], [py])

    A.value = 10
    B.value = 11
    C.value = 12
    generate_kernel_test_case(
        description=f"[chainer] F.elu with placeholder",
        graph=graph,
        backend=["webgpu", "webassembly"],
        inputs={graph.inputs[0]: vx.data},
        expected={graph.outputs[0]: vy.data},
    )
