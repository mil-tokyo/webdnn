import chainer
import numpy as np

from test.util import generate_kernel_test_case
from webdnn.frontend.chainer.converter import ChainerConverter
from webdnn.graph.order import OrderNCHW
from webdnn.graph.variables.constant_variable import ConstantVariable


def test():
    link = chainer.links.Convolution2D(4, 10, ksize=3, stride=1, pad=1)

    vx = chainer.Variable(np.random.rand(2, 4, 6, 8).astype(np.float32))
    vy = link(vx)

    graph = ChainerConverter().convert_from_inout_vars([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] L.Convolution2D",
        graph=graph,
        inputs={x: ConstantVariable(vx.data, OrderNCHW).change_order(x.order).data},
        expected={y: ConstantVariable(vy.data, OrderNCHW).change_order(y.order).data}
    )


def test_nobias():
    link = chainer.links.Convolution2D(4, 10, ksize=3, stride=1, pad=1, nobias=True)

    vx = chainer.Variable(np.random.rand(2, 4, 6, 8).astype(np.float32))
    vy = link(vx)

    graph = ChainerConverter().convert_from_inout_vars([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] L.Convolution2D(nobias=True)",
        graph=graph,
        inputs={x: ConstantVariable(vx.data, OrderNCHW).change_order(x.order).data},
        expected={y: ConstantVariable(vy.data, OrderNCHW).change_order(y.order).data}
    )
