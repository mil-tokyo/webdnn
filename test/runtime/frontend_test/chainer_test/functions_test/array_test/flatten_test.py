import chainer
import numpy as np
from webdnn.frontend.chainer.converter import ChainerConverter

from test.util import generate_kernel_test_case, wrap_template


@wrap_template
def template(x_shape=(2, 4, 6, 8), description=""):
    vx = chainer.Variable(np.random.rand(*x_shape).astype(np.float32))
    vy = chainer.functions.flatten(vx)

    graph = ChainerConverter().convert([vx], [vy])

    assert list(graph.outputs[0].shape) == list(vy.shape)
    generate_kernel_test_case(
        description=f"[chainer] F.flatten {description}",
        graph=graph,
        backend=["webgpu", "webgl", "webassembly"],
        inputs={graph.inputs[0]: vx.data},
        expected={graph.outputs[0]: vy.data},
    )


def test_general():
    template()


def test_flat():
    template(x_shape=(20,))
