import chainer
import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn.frontend.chainer.converter import ChainerConverter


@wrap_template
def template(x_shape, description=""):
    vx = chainer.Variable(np.random.rand(*x_shape).astype(np.float32))
    vy = chainer.functions.flipud(vx)

    graph = ChainerConverter().convert([vx], [vy])

    assert list(graph.outputs[0].shape) == list(vy.shape)
    generate_kernel_test_case(
        description=f"[chainer] F.flipud {description}",
        graph=graph,
        backend=["webgpu", "webgl", "webassembly"],
        inputs={graph.inputs[0]: vx.data},
        expected={graph.outputs[0]: vy.data},
    )


def test_2d():
    template(x_shape=[3, 4])


def test_3d():
    template(x_shape=[3, 4, 5])
