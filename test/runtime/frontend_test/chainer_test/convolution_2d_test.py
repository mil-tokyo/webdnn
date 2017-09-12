import chainer
import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn.frontend.chainer.converter import ChainerConverter


@wrap_template
def template(n=2, c_in=4, h_in=6, w_in=8, c_out=10, ksize=3, stride=1, pad=0, nobias=True, description=""):
    link = chainer.links.Convolution2D(c_in, c_out, ksize=ksize, stride=stride, pad=pad, nobias=nobias)
    link.W.data = np.random.rand(*link.W.shape).astype(np.float32)
    vx = chainer.Variable(np.random.rand(*(n, c_in, h_in, w_in)).astype(np.float32))
    vy = link(vx)

    graph = ChainerConverter().convert([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] L.Convolution2D {description}",
        graph=graph,
        inputs={x: vx.data},
        expected={y: vy.data}
    )


def test():
    template()


def test_nobias():
    template(nobias=True)


def test_nopadding():
    template(pad=0)


def test_irregular_kernel_size():
    template(ksize=(3, 4))


def test_irregular_stride_size():
    template(stride=(2, 3))


def test_irregular_padding_size1():
    template(pad=(1, 2))


def test_irregular_padding_size2():
    template(pad=2)


def test_irregular_padding_size3():
    template(pad=2, ksize=5)


def test_irregular_padding_size4():
    template(pad=(1, 0))


def test_irregular_size():
    template(ksize=(3, 5), stride=(2, 3), pad=(1, 3))


def test_special_size():
    # https://github.com/mil-tokyo/webdnn/issues/525
    # In case that the position index (=n*c_in*h_in*w_in*ksize*ksize)  >  1<<23
    template(n=1, c_in=64, h_in=128, w_in=128, c_out=3, ksize=9, pad=4)
