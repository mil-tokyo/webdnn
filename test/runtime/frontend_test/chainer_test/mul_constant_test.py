import chainer
import numpy as np

from test.util import generate_kernel_test_case
from webdnn.frontend.chainer.converter import ChainerConverter


def test():
    vx = chainer.Variable(np.random.rand(2, 4, 6, 8))
    vy = vx * 2

    graph = ChainerConverter().convert([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] F.MulConstant",
        graph=graph,
        inputs={x: vx.data},
        expected={y: vy.data},
    )


def test_rmul():
    vx = chainer.Variable(np.random.rand(2, 4, 6, 8))
    vy = 2 * vx

    graph = ChainerConverter().convert([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] F.MulConstant rmul",
        graph=graph,
        inputs={x: vx.data},
        expected={y: vy.data},
    )
