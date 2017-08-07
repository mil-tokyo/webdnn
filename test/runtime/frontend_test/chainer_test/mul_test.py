import chainer
import numpy as np

from test.util import generate_kernel_test_case
from webdnn.frontend.chainer.converter import ChainerConverter


def test():
    vx1 = chainer.Variable(np.random.rand(2, 4, 6, 8))
    vx2 = chainer.Variable(np.random.rand(2, 4, 6, 8))
    vy = vx1 * vx2

    graph = ChainerConverter().convert([vx1, vx2], [vy])

    x1 = graph.inputs[0]
    x2 = graph.inputs[1]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] F.Mul",
        graph=graph,
        inputs={
            x1: vx1.data,
            x2: vx2.data
        },
        expected={y: vy.data},
    )


def test_itself():
    vx = chainer.Variable(np.random.rand(2, 4, 6, 8))
    vy = vx * vx

    graph = ChainerConverter().convert([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] F.Mul itself",
        graph=graph,
        inputs={x: vx.data},
        expected={y: vy.data},
    )
