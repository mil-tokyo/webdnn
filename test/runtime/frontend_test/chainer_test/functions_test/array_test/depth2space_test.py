import chainer
import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn import Placeholder
from webdnn.frontend.chainer.converter import ChainerConverter
from webdnn.frontend.chainer.placeholder_variable import PlaceholderVariable


@wrap_template
def template(r=2, description=""):
    vx = chainer.Variable(np.random.rand(2, 4 * r * r, 6, 8).astype(np.float32))
    vy = chainer.functions.depth2space(vx, r)

    graph = ChainerConverter().convert([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] F.Depth2Space {description}",
        graph=graph,
        backend=["webgpu", "webgl", "webassembly"],
        inputs={x: vx.data},
        expected={y: vy.data},
    )


def test():
    template()


def test_r_3():
    template(r=3)


def test_with_placeholder():
    vx = chainer.Variable(np.random.rand(2, 20, 4, 8).astype(np.float32))
    vy = chainer.functions.depth2space(vx, r=2)

    N = Placeholder(label="N")
    H = Placeholder(label="H")
    W = Placeholder(label="W")
    px = PlaceholderVariable([N, 20, H, W])
    py = chainer.functions.depth2space(px, r=2)

    graph = ChainerConverter().convert([px], [py])

    N.value = 2
    H.value = 4
    W.value = 8
    generate_kernel_test_case(
        description=f"[chainer] F.depth2space with placeholder",
        graph=graph,
        backend=["webgpu", "webassembly"],
        inputs={graph.inputs[0]: vx.data},
        expected={graph.outputs[0]: vy.data},
    )
