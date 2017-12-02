from unittest import SkipTest

import chainer
import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn.frontend.chainer.converter import ChainerConverter


@wrap_template
def template(x_shape=(2, 3, 16, 16), ksize=3, stride=1, pad=1, dilate=1, description=""):
    if chainer.__version__ < "2.":
        raise SkipTest("chainer.functions.im2col is not exist in this version of Chainer.")

    vx = chainer.Variable(np.random.rand(*x_shape).astype(np.float32))
    vy = chainer.functions.im2col(vx, ksize=ksize, stride=stride, pad=pad, dilate=dilate)

    graph = ChainerConverter().convert([vx], [vy])

    assert list(graph.outputs[0].shape) == list(vy.shape), f"{list(graph.outputs[0].shape)}, {list(vy.shape)}"
    generate_kernel_test_case(
        description=f"[chainer] F.im2col {description}",
        graph=graph,
        backend=["webgpu", "webgl", "webassembly"],
        inputs={graph.inputs[0]: vx.data},
        expected={graph.outputs[0]: vy.data},
    )


def test():
    template()


def test_projection_ksize():
    template(ksize=1, stride=1, pad=0)


def test_odd_ksize():
    template(ksize=(3, 4))


def test_odd_padding():
    template(pad=(3, 4))


def test_no_padding():
    template(pad=0)


def test_odd_stride():
    template(stride=(2, 2))


def test_odd_dilate():
    template(ksize=(1, 2))
