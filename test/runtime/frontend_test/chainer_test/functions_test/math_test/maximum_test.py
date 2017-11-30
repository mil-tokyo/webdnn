import chainer
import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn.frontend.chainer.converter import ChainerConverter


@wrap_template
def template(description: str = ""):
    vx0 = chainer.Variable(np.random.rand(2, 5, 6, 8).astype(np.float32))
    vx1 = chainer.Variable(np.random.rand(2, 5, 6, 8).astype(np.float32))
    vy = chainer.functions.maximum(vx0, vx1)

    graph = ChainerConverter().convert([vx0, vx1], [vy])

    x0 = graph.inputs[0]
    x1 = graph.inputs[1]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] F.maximum {description}",
        graph=graph,
        inputs={x0: vx0.data, x1: vx1.data},
        expected={y: vy.data},
    )


def test():
    template()
