import chainer
import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn.frontend.chainer.converter import ChainerConverter


@wrap_template
def template(x_shape, axis1, axis2, description=""):
    vx = chainer.Variable(np.random.rand(*x_shape).astype(np.float32))
    vy = chainer.functions.swapaxes(vx, axis1=axis1, axis2=axis2)

    graph = ChainerConverter().convert([vx], [vy])

    assert list(graph.outputs[0].shape) == list(vy.shape)
    generate_kernel_test_case(
        description=f"[chainer] F.swapaxes {description}",
        graph=graph,
        backend=["webgpu", "webassembly", "webgl"],
        inputs={graph.inputs[0]: vx.data},
        expected={graph.outputs[0]: vy.data},
    )


def test():
    template(x_shape=[3, 4, 5, 6], axis1=0, axis2=2)


def test_inverse():
    template(x_shape=[3, 4, 5, 6], axis1=2, axis2=0)


def test_same_axis():
    template(x_shape=[3, 4, 5, 6], axis1=2, axis2=2)
