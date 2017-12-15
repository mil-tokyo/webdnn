import chainer
import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn import Placeholder
from webdnn.frontend.chainer.converter import ChainerConverter
from webdnn.frontend.chainer.placeholder_variable import PlaceholderVariable


@wrap_template
def template(x_shape=[2, 3, 4, 5], description: str = ""):
    vx = chainer.Variable(np.random.rand(*x_shape).astype(np.float32))
    vy = chainer.functions.log_softmax(vx)

    graph = ChainerConverter().convert([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] F.log_softmax {description}",
        graph=graph,
        backend=["webgpu", "webassembly", "webgl"],
        inputs={x: vx.data},
        expected={y: vy.data},
        EPS=1e-2
    )


def test_2d():
    template(x_shape=[5, 10])


def test_3d():
    template(x_shape=[5, 10, 15])


def test_4d():
    template(x_shape=[2, 3, 4, 5])


def test_with_placeholder():
    vx = chainer.Variable(np.random.rand(10, 11, 12).astype(np.float32))
    vy = chainer.functions.log_softmax(vx)

    A = Placeholder(label="A")
    C = Placeholder(label="C")
    px = PlaceholderVariable([A, 11, C])
    py = chainer.functions.log_softmax(px)

    graph = ChainerConverter().convert([px], [py])

    A.value = 10
    C.value = 12
    generate_kernel_test_case(
        description=f"[chainer] F.log_softmax with placeholder",
        graph=graph,
        backend=["webgpu", "webassembly"],
        inputs={graph.inputs[0]: vx.data},
        expected={graph.outputs[0]: vy.data},
        EPS=1e-2
    )
