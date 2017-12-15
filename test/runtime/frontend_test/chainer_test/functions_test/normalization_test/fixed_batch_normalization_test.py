from unittest import SkipTest

import chainer
import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn import Placeholder
from webdnn.frontend.chainer.converter import ChainerConverter
from webdnn.frontend.chainer.placeholder_variable import PlaceholderVariable


@wrap_template
def template(description=""):
    if chainer.__version__ < "3.":
        raise SkipTest("F.fixed_batch_normalization is supported since Chainer v3.0.")

    link = chainer.links.BatchNormalization(size=4)
    vx = chainer.Variable(np.random.rand(2, 4, 6, 8).astype(np.float32))

    with chainer.using_config('train', False):
        vy = link(vx)

    graph = ChainerConverter().convert([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] F.FixedBatchNormalization {description}",
        graph=graph,
        inputs={x: vx.data},
        expected={y: vy.data}
    )


def test():
    template()


def test_with_placeholder():
    link = chainer.links.BatchNormalization(size=3)
    vx = chainer.Variable(np.random.rand(1, 3, 16, 16).astype(np.float32))
    with chainer.using_config('train', False):
        vy = link(vx)

    N = Placeholder(label="N")
    H = Placeholder(label="H")
    W = Placeholder(label="W")
    px = PlaceholderVariable([N, 3, H, W])
    with chainer.using_config('train', False):
        py = link(px)

    graph = ChainerConverter().convert([px], [py])

    x = graph.inputs[0]
    y = graph.outputs[0]

    N.value = 1
    H.value = 16
    W.value = 16
    generate_kernel_test_case(
        description=f"[chainer] L.FixedBatchNormalization with placeholder",
        graph=graph,
        backend=["webgpu", "webassembly"],
        inputs={x: vx.data},
        expected={y: vy.data},
    )
