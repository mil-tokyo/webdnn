import chainer
import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn.frontend.chainer.converter import ChainerConverter


@wrap_template
def template(z=0.5, description=""):
    vx = chainer.Variable(np.random.rand(2, 4, 6, 8).astype(np.float32))
    vy = chainer.functions.clipped_relu(vx, z=z)

    graph = ChainerConverter().convert([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] F.clipped_relu {description}",
        graph=graph,
        inputs={x: vx.data},
        expected={y: vy.data}
    )


def test():
    template()


def test_z_1():
    template(z=1.0)
