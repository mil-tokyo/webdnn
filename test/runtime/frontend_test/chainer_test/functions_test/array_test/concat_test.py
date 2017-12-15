import chainer
import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn import Placeholder
from webdnn.frontend.chainer.converter import ChainerConverter
from webdnn.frontend.chainer.placeholder_variable import PlaceholderVariable


@wrap_template
def template(shape1=(2, 3, 4, 5), shape2=(6, 3, 4, 5), axis=0, description=""):
    vx1 = chainer.Variable(np.random.rand(*shape1).astype(np.float32))
    vx2 = chainer.Variable(np.random.rand(*shape2).astype(np.float32))
    vy = chainer.functions.concat([vx1, vx2], axis=axis)

    graph = ChainerConverter().convert([vx1, vx2], [vy])

    x1, x2 = graph.inputs
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] F.Concat {description}",
        graph=graph,
        inputs={
            x1: vx1.data,
            x2: vx2.data,
        },
        expected={y: vy.data}
    )


def test():
    template()


def test_middle_axis():
    template(shape1=(2, 3, 4, 5), shape2=(2, 6, 4, 5), axis=1)


def test_last_axis():
    template(shape1=(2, 3, 4, 5), shape2=(2, 3, 4, 6), axis=3)


def test_with_placeholder():
    vx1 = chainer.Variable(np.random.rand(2, 10, 4, 5).astype(np.float32))
    vx2 = chainer.Variable(np.random.rand(2, 15, 4, 5).astype(np.float32))
    vy = chainer.functions.concat([vx1, vx2], axis=1)

    N = Placeholder(label="N")
    C1 = Placeholder(label="C1")
    C2 = Placeholder(label="C2")
    H = Placeholder(label="H")
    W = Placeholder(label="W")
    px1 = PlaceholderVariable([N, C1, H, W])
    px2 = PlaceholderVariable([N, C2, H, W])
    py = chainer.functions.concat([px1, px2], axis=1)

    graph = ChainerConverter().convert([px1, px2], [py])

    N.value = 2
    C1.value = 10
    C2.value = 15
    H.value = 4
    W.value = 5
    generate_kernel_test_case(
        description=f"[chainer] F.concat with placeholder",
        graph=graph,
        backend=["webgpu", "webassembly"],
        inputs={graph.inputs[0]: vx1.data, graph.inputs[1]: vx2.data},
        expected={graph.outputs[0]: vy.data},
    )
