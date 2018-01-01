import chainer
import numpy as np
from nose import with_setup

from test.util import generate_kernel_test_case
from webdnn.frontend.chainer.converter import ChainerConverter
from webdnn.util import config

_original_max_texture_size = 0


def _set_texture_size(max_texture_size: int = 4096):
    def handler():
        config.WEBGL_MAX_TEXTURE_SIZE = max_texture_size

    return handler


def generate_array(*shape):
    # return np.arange(np.product(shape)).reshape(shape).astype(np.float32)
    return np.random.rand(*shape).astype(np.float32)


@with_setup(_set_texture_size(4096), _set_texture_size(config.WEBGL_MAX_TEXTURE_SIZE))
def test_sgemm_largeN():
    M = 64
    K = 512
    N = config.WEBGL_MAX_TEXTURE_SIZE * 2
    A = chainer.Variable(generate_array(M, K))
    B = chainer.Variable(generate_array(N, K))

    C = chainer.functions.linear(A, B)

    graph = ChainerConverter().convert([A], [C])

    generate_kernel_test_case(
        description=f"test_sgemm_large_N",
        graph=graph,
        backend=["webgl"],
        inputs={graph.inputs[0]: A.data},
        expected={graph.outputs[0]: C.data},
    )


@with_setup(_set_texture_size(4096), _set_texture_size(config.WEBGL_MAX_TEXTURE_SIZE))
def test_sgemm_largeK():
    M = config.WEBGL_MAX_TEXTURE_SIZE
    K1 = config.WEBGL_MAX_TEXTURE_SIZE
    K2 = config.WEBGL_MAX_TEXTURE_SIZE
    N = 64
    A1 = chainer.Variable(generate_array(M, K1))
    A2 = chainer.Variable(generate_array(M, K2))
    B = chainer.Variable(generate_array(N, K1 + K2))

    C = chainer.functions.linear(chainer.functions.concat([A1, A2], axis=1), B)

    graph = ChainerConverter().convert([A1, A2], [C])

    generate_kernel_test_case(
        description=f"test_sgemm_large_K",
        graph=graph,
        backend=["webgl"],
        inputs={graph.inputs[0]: A1.data, graph.inputs[1]: A2.data},
        expected={graph.outputs[0]: C.data},
    )


@with_setup(_set_texture_size(4096), _set_texture_size(config.WEBGL_MAX_TEXTURE_SIZE))
def test_sgemm_largeM():
    M1 = config.WEBGL_MAX_TEXTURE_SIZE
    M2 = config.WEBGL_MAX_TEXTURE_SIZE
    K = config.WEBGL_MAX_TEXTURE_SIZE
    N = 64
    A1 = chainer.Variable(generate_array(M1, K))
    A2 = chainer.Variable(generate_array(M2, K))
    B = chainer.Variable(generate_array(N, K))

    C = chainer.functions.linear(chainer.functions.concat([A1, A2], axis=0), B)

    graph = ChainerConverter().convert([A1, A2], [C])

    generate_kernel_test_case(
        description=f"test_sgemm_large_M",
        graph=graph,
        backend=["webgl"],
        inputs={graph.inputs[0]: A1.data, graph.inputs[1]: A2.data},
        expected={graph.outputs[0]: C.data},
    )


@with_setup(_set_texture_size(4096), _set_texture_size(config.WEBGL_MAX_TEXTURE_SIZE))
def test_convolution2d_large_C1_1():
    # case that C1 < MAX_TEXTURE_SIZE < C1*KH*KW

    H1 = 8
    W1 = 8
    C1 = config.WEBGL_MAX_TEXTURE_SIZE // 8
    C2 = 3

    link = chainer.links.Convolution2D(C1, C2, ksize=3, stride=1, pad=1, nobias=True)
    link.W.data = generate_array(*link.W.shape)
    vx = chainer.Variable(generate_array(1, C1, H1, W1).astype(np.float32))
    vy = link(vx)

    graph = ChainerConverter().convert([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"test_convolution2d_large_C1_1",
        graph=graph,
        backend=["webgl"],
        inputs={x: vx.data},
        expected={y: vy.data}
    )


@with_setup(_set_texture_size(4096), _set_texture_size(config.WEBGL_MAX_TEXTURE_SIZE))
def test_convolution2d_large_C1_2():
    # case that MAX_TEXTURE_SIZE < C1
    H1 = 8
    W1 = 8
    C1 = config.WEBGL_MAX_TEXTURE_SIZE
    C2 = 3

    link = chainer.links.Convolution2D(C1, C2, ksize=3, stride=1, pad=1, nobias=True)
    link.W.data = generate_array(*link.W.shape)
    vx = chainer.Variable(generate_array(1, C1, H1, W1).astype(np.float32))
    vy = link(vx)

    graph = ChainerConverter().convert([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"test_convolution2d_large_C1_2",
        graph=graph,
        backend=["webgl"],
        inputs={x: vx.data},
        expected={y: vy.data}
    )


@with_setup(_set_texture_size(4096), _set_texture_size(config.WEBGL_MAX_TEXTURE_SIZE))
def test_convolution2d_large_HW():
    H1 = 128
    W1 = 128
    C1 = 2
    C2 = 2

    link = chainer.links.Convolution2D(C1, C2, ksize=3, stride=1, pad=1, nobias=True)
    link.W.data = generate_array(*link.W.shape)
    vx = chainer.Variable(generate_array(1, C1, H1, W1))
    vy = link(vx)

    graph = ChainerConverter().convert([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"test_convolution2d_large_HW",
        graph=graph,
        backend=["webgl"],
        inputs={x: vx.data},
        expected={y: vy.data}
    )


@with_setup(_set_texture_size(4096), _set_texture_size(config.WEBGL_MAX_TEXTURE_SIZE))
def test_tensorwise():
    x1 = chainer.Variable(generate_array(1, 4096))
    x2 = chainer.Variable(generate_array(1, 4096))
    h = chainer.functions.concat([x1, x2], axis=1)
    h = h + 1
    link = chainer.links.Linear(8192, 1)
    link.W.data = generate_array(*link.W.shape)
    y = link(h)

    graph = ChainerConverter().convert([x1], [y])

    generate_kernel_test_case(
        description=f"test_tensorwise",
        graph=graph,
        backend=["webgl"],
        inputs={graph.inputs[0]: x1.data},
        expected={graph.outputs[0]: y.data}
    )
