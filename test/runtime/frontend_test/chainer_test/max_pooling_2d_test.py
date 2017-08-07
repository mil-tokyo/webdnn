import chainer
import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn.frontend.chainer.converter import ChainerConverter


@wrap_template
def template(ksize=2, stride=None, pad=0, description=""):
    vx = chainer.Variable(np.random.rand(2, 4, 6, 8))
    vy = chainer.functions.max_pooling_2d(vx, ksize=ksize, stride=stride, pad=pad)

    graph = ChainerConverter().convert([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] F.max_pooling_2d {description}",
        graph=graph,
        inputs={x: vx.data},
        expected={y: vy.data},
    )


def test():
    template()


def test_padding_not_zero():
    template(pad=1)


def test_stride_is_none():
    template(stride=None, pad=1)


def test_irregular_size():
    template(ksize=(3, 4), stride=(1, 2), pad=(1, 3))
