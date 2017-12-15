import chainer
import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn import Placeholder
from webdnn.frontend.chainer.converter import ChainerConverter
from webdnn.frontend.chainer.placeholder_variable import PlaceholderVariable


@wrap_template
def template(description: str = ""):
    vx = chainer.Variable(np.random.rand(2, 5, 6, 8).astype(np.float32))
    vy = chainer.functions.cosh(vx)

    graph = ChainerConverter().convert([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] F.cosh {description}",
        graph=graph,
        inputs={x: vx.data},
        expected={y: vy.data},
        EPS=1e-2
    )


def test():
    template()


def test_with_placeholder():
    vx = chainer.Variable(np.random.rand(10, 11, 12).astype(np.float32))
    vy = chainer.functions.cosh(vx)

    A = Placeholder(label="A")
    B = Placeholder(label="B")
    C = Placeholder(label="C")
    px = PlaceholderVariable([A, B, C])
    py = chainer.functions.cosh(px)

    graph = ChainerConverter().convert([px], [py])

    A.value = 10
    B.value = 11
    C.value = 12
    generate_kernel_test_case(
        description=f"[chainer] F.cosh with placeholder",
        graph=graph,
        backend=["webgpu", "webassembly"],
        inputs={graph.inputs[0]: vx.data},
        expected={graph.outputs[0]: vy.data},
        EPS=1e-2
    )
