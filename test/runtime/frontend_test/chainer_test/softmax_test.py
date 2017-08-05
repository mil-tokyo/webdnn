import chainer
import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn.frontend.chainer.converter import ChainerConverter
from webdnn.graph.order import OrderNC, OrderNCHW
from webdnn.util.misc import mul

default_order = {
    2: OrderNC,
    4: OrderNCHW
}


@wrap_template
def template(axis=1, ndim=2, description: str = ""):
    shape = (np.arange(ndim, ) + 2).tolist()
    vx = chainer.Variable(np.arange(mul(shape)).reshape(shape).astype(np.float32))
    vy = chainer.functions.softmax(vx, axis)

    graph = ChainerConverter().convert([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] F.softmax {description}",
        graph=graph,
        inputs={x: vx.data},
        backend=["webgpu", "webassembly"],
        expected={y: vy.data},
    )


def test():
    template()


def test_axis_first_axis():
    template(axis=0)


def test_4d_first_axis():
    template(axis=0, ndim=4)


def test_4d_middle_axis():
    template(axis=1, ndim=4)


def test_4d_last_axis():
    template(axis=3, ndim=4)
