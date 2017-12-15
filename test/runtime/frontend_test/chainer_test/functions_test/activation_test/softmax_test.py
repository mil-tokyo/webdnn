from unittest import SkipTest

import chainer
import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn import Placeholder
from webdnn.frontend.chainer.converter import ChainerConverter
from webdnn.frontend.chainer.placeholder_variable import PlaceholderVariable
from webdnn.graph.order import OrderNC, OrderNCHW
from webdnn.util.misc import mul

default_order = {
    2: OrderNC,
    4: OrderNCHW
}


@wrap_template
def template(axis=1, ndim=2, description: str = ""):
    if chainer.__version__ < "1.24" and axis != 1:
        raise SkipTest(
            f"chainer.functions.softmax support \"xis\" parameter since v1.24, current installed version is {chainer.__version__}")

    shape = (np.arange(ndim, ) + 2).tolist()
    vx = chainer.Variable(np.arange(mul(shape)).reshape(shape).astype(np.float32))

    if chainer.__version__ < "1.24":
        vy = chainer.functions.softmax(vx)

    else:
        vy = chainer.functions.softmax(vx, axis=axis)

    graph = ChainerConverter().convert([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] F.softmax {description}",
        graph=graph,
        backend=["webgpu", "webassembly"],
        inputs={x: vx.data},
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


def test_with_placeholder():
    vx = chainer.Variable(np.random.rand(10, 11, 12).astype(np.float32))
    vy = chainer.functions.softmax(vx, axis=1)

    A = Placeholder(label="A")
    B = Placeholder(label="B")
    C = Placeholder(label="C")
    px = PlaceholderVariable([A, B, C])
    py = chainer.functions.softmax(px, axis=1)

    graph = ChainerConverter().convert([px], [py])

    A.value = 10
    B.value = 11
    C.value = 12
    generate_kernel_test_case(
        description=f"[chainer] F.softmax with placeholder",
        graph=graph,
        backend=["webgpu", "webassembly"],
        inputs={graph.inputs[0]: vx.data},
        expected={graph.outputs[0]: vy.data},
    )
