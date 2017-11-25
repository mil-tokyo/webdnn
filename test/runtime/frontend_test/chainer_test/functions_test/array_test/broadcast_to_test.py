import chainer
import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn.frontend.chainer.converter import ChainerConverter


@wrap_template
def template(shape=None, description=""):
    if shape is None:
        shape = [2, 4, 6, 8]

    vx = chainer.Variable(np.random.rand(2, 1, 1, 8).astype(np.float32))
    vy = chainer.functions.broadcast_to(vx, shape=shape)

    graph = ChainerConverter().convert([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] F.broadcast_to {description}",
        graph=graph,
        inputs={x: vx.data},
        expected={y: vy.data}
    )


def test():
    template()
