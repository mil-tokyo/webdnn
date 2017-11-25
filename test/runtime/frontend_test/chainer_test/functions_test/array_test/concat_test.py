import chainer
import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn.frontend.chainer.converter import ChainerConverter


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
        backend=["webgpu", "webassembly"],
        expected={y: vy.data}
    )


def test():
    template()


def test_middle_axis():
    template(shape1=(2, 3, 4, 5), shape2=(2, 6, 4, 5), axis=1)


def test_last_axis():
    template(shape1=(2, 3, 4, 5), shape2=(2, 3, 4, 6), axis=3)
