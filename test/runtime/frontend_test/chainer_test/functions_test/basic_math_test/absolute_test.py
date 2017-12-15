import chainer
import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn import Placeholder
from webdnn.frontend.chainer.converter import ChainerConverter
from webdnn.frontend.chainer.placeholder_variable import PlaceholderVariable


@wrap_template
def template(description=""):
    vx = chainer.Variable(np.random.rand(2, 4, 6, 8).astype(np.float32) - 0.5)
    vy = abs(vx)

    graph = ChainerConverter().convert([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] F.Abs {description}",
        graph=graph,
        inputs={x: vx.data},
        expected={y: vy.data},
    )


def test():
    template()


def test_with_placeholder():
    vx = chainer.Variable(np.random.rand(1, 3, 16, 16).astype(np.float32))
    vy = abs(vx)

    H = Placeholder(label="H")
    W = Placeholder(label="W")
    px = PlaceholderVariable([1, 3, H, W])
    py = abs(px)

    graph = ChainerConverter().convert([px], [py])

    x = graph.inputs[0]
    y = graph.outputs[0]

    H.value = 16
    W.value = 16
    generate_kernel_test_case(
        description=f"[chainer] F.Abs with placeholder",
        graph=graph,
        backend=["webgpu", "webassembly"],
        inputs={x: vx.data},
        expected={y: vy.data},
    )
