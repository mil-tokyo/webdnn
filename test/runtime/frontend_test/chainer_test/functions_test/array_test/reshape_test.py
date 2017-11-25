import chainer
import numpy as np
from webdnn.frontend.chainer.converter import ChainerConverter

from test.util import generate_kernel_test_case, wrap_template


@wrap_template
def template(x_shape=(2, 6, 10, 12), new_shape=(3, 5, 3, 32), description=""):
    vx = chainer.Variable(np.random.rand(*x_shape).astype(np.float32))
    vy = chainer.functions.reshape(vx, new_shape)

    graph = ChainerConverter().convert([vx], [vy])

    assert list(graph.outputs[0].shape) == list(vy.shape)
    generate_kernel_test_case(
        description=f"[chainer] F.reshape {description}",
        graph=graph,
        backend=["webgpu", "webgl", "webassembly"],
        inputs={graph.inputs[0]: vx.data},
        expected={graph.outputs[0]: vy.data},
    )


def test_general():
    template()


def test_same_shape():
    template(x_shape=(2, 10), new_shape=(2, 10))
