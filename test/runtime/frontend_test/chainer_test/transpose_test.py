import chainer
import numpy as np

from test.util import generate_kernel_test_case
from webdnn.frontend.chainer.converter import ChainerConverter


def test():
    """
    Transpose test

    Chainer assumes variable order for convolution as NCHW.
    Reshape assumes no memory operation.
    However, WebDNN currently accepts only NHWC.
    Transpose have to be automatically inserted to work convolution and reshape correctly.

    Returns:

    """
    vx = chainer.Variable(np.random.rand(2, 4, 6, 8).astype(np.float32))
    conv1 = chainer.links.Convolution2D(4, 10, ksize=3)
    conv2 = chainer.links.Convolution2D(2, 4, ksize=5)
    linear1 = chainer.links.Linear(None, 5)
    h = conv1(vx)  # (2, 10, 4, 6)
    h = chainer.functions.reshape(h, (1, 2, 8, 30))
    h = conv2(h)  # (1, 4, 4, 26)
    h = chainer.functions.max_pooling_2d(h, ksize=2, stride=2)  # (1, 4, 2, 13)
    h = chainer.functions.reshape(h, (1, 2, 2, 26))
    # implicit reshape to (1, 2*2*26)
    vy = linear1(h)

    graph = ChainerConverter().convert([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] insertion of transposition",
        graph=graph,
        inputs={x: vx.data},
        expected={y: vy.data},
        backend=["webgpu", "webassembly"]
    )
