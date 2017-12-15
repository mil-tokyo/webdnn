from unittest import SkipTest

import chainer
import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn import Placeholder
from webdnn.frontend.chainer.converter import ChainerConverter
from webdnn.frontend.chainer.placeholder_variable import PlaceholderVariable


@wrap_template
def template(axis, keepdims, description: str = ""):
    if chainer.__version__ < "1.24" and keepdims:
        raise SkipTest(
            f"chainer.functions.sum support \"keepdims\" parameter since v1.24, current installed version is {chainer.__version__}")

    vx = chainer.Variable(np.random.rand(2, 5, 6, 8).astype(np.float32))

    if chainer.__version__ < "1.24":
        vy = chainer.functions.sum(vx, axis=axis)

    else:
        vy = chainer.functions.sum(vx, axis=axis, keepdims=keepdims)

    graph = ChainerConverter().convert([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    assert list(vy.shape) == list(y.shape), f"{vy.shape}, {y.shape}"
    generate_kernel_test_case(
        description=f"[chainer] F.sum {description}",
        graph=graph,
        backend=["webgpu", "webgl", "webassembly"],
        inputs={x: vx.data},
        expected={y: vy.data},
    )


def test_axis_tuple():
    template(axis=(1, 3), keepdims=True)


def test_axis_int():
    template(axis=1, keepdims=True)


def test_axis_none():
    template(axis=None, keepdims=True)


def test_no_keepdims():
    template(axis=(1, 3), keepdims=False)


def test_with_placeholder():
    vx = chainer.Variable(np.random.rand(10, 11, 12).astype(np.float32))
    vy = chainer.functions.sum(vx, axis=1, keepdims=False)

    A = Placeholder(label="A")
    B = Placeholder(label="B")
    C = Placeholder(label="C")
    px = PlaceholderVariable([A, B, C])
    py = chainer.functions.sum(px, axis=1, keepdims=False)

    graph = ChainerConverter().convert([px], [py])

    A.value = 10
    B.value = 11
    C.value = 12
    generate_kernel_test_case(
        description=f"[chainer] F.sum with placeholder",
        graph=graph,
        backend=["webgpu", "webassembly"],
        inputs={graph.inputs[0]: vx.data},
        expected={graph.outputs[0]: vy.data},
    )
