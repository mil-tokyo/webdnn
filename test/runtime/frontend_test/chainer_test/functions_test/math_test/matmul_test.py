import chainer
import numpy as np
from webdnn.frontend.chainer.converter import ChainerConverter

from test.util import generate_kernel_test_case, wrap_template


@wrap_template
def template(a_shape=(2, 4), b_shape=(4, 6), transa=False, transb=False, description: str = ""):
    vx1 = chainer.Variable(np.random.rand(*a_shape).astype(np.float32))
    vx2 = chainer.Variable(np.random.rand(*b_shape).astype(np.float32))
    vy = chainer.functions.matmul(vx1, vx2, transa=transa, transb=transb)

    graph = ChainerConverter().convert([vx1, vx2], [vy])

    x1 = graph.inputs[0]
    x2 = graph.inputs[1]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] F.MatMul {description}",
        graph=graph,
        inputs={
            x1: vx1.data,
            x2: vx2.data
        },
        expected={y: vy.data},
    )


def test_NN():
    template(a_shape=(2, 4), b_shape=(4, 6), transa=False, transb=False)


def test_NT():
    template(a_shape=(2, 4), b_shape=(6, 4), transa=False, transb=True)


def test_TN():
    template(a_shape=(4, 2), b_shape=(4, 6), transa=True, transb=False)


def test_TT():
    template(a_shape=(4, 2), b_shape=(6, 4), transa=True, transb=True)


def test_itself():
    vx = chainer.Variable(np.random.rand(8, 8))
    vy = chainer.functions.matmul(vx, vx, False, False)

    graph = ChainerConverter().convert([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] F.MatMul itself",
        graph=graph,
        inputs={x: vx.data},
        expected={y: vy.data},
    )
