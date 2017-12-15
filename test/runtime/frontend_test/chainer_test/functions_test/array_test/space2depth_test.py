import chainer
import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn import Placeholder
from webdnn.frontend.chainer.converter import ChainerConverter
from webdnn.frontend.chainer.placeholder_variable import PlaceholderVariable


@wrap_template
def template(r=2, description=""):
    vx = chainer.Variable(np.random.rand(2, 4, 6 * r, 8 * r).astype(np.float32))
    vy = chainer.functions.space2depth(vx, r)

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
    vx = chainer.Variable(np.random.rand(2, 5, 4, 8).astype(np.float32))
    vy = chainer.functions.space2depth(vx, r=2)

    N = Placeholder(label="N")
    C = Placeholder(label="C")
    px = PlaceholderVariable([N, C, 4, 8])
    py = chainer.functions.space2depth(px, r=2)

    graph = ChainerConverter().convert([px], [py])

    N.value = 2
    C.value = 5
    generate_kernel_test_case(
        description=f"[chainer] F.space2depth with placeholder",
        graph=graph,
        backend=["webgpu", "webassembly"],
        inputs={graph.inputs[0]: vx.data},
        expected={graph.outputs[0]: vy.data},
    )
