import chainer
import numpy as np
from webdnn.frontend.chainer.converter import ChainerConverter

from test.util import generate_kernel_test_case


def template(vx, vy, description: str = ""):
    graph = ChainerConverter().convert([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] F.MulConstant {description}",
        graph=graph,
        inputs={x: vx.data},
        expected={y: vy.data},
    )


def test_mul():
    vx = chainer.Variable(np.random.rand(2, 4, 6, 8).astype(np.float32))
    vy = vx * 2
    template(vx, vy, "lhs")


def test_rmul():
    vx = chainer.Variable(np.random.rand(2, 4, 6, 8))
    vy = 2 * vx
    template(vx, vy, "rhs")
