import chainer
import numpy as np
from webdnn.frontend.chainer.converter import ChainerConverter

from test.util import generate_kernel_test_case, wrap_template


@wrap_template
def template(x_shape=(2, 5, 6, 8), slope=0.5, description: str = ""):
    vx = chainer.Variable(np.random.rand(*x_shape).astype(np.float32))
    vy = chainer.functions.leaky_relu(vx, slope)

    graph = ChainerConverter().convert([vx], [vy])

    generate_kernel_test_case(
        description=f"[chainer] F.leaky_relu {description}",
        graph=graph,
        inputs={graph.inputs[0]: vx.data},
        expected={graph.outputs[0]: vy.data},
    )


def test():
    template()


def test_no_slope():
    template(slope=0)
