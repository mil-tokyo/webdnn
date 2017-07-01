import chainer
import numpy as np

from test.util import generate_kernel_test_case
from webdnn.frontend.chainer import ChainerConverter
from webdnn.graph.order import OrderNCHW
from webdnn.graph.variables.constant_variable import ConstantVariable


def test_dilate_is_1():
    link = chainer.links.DilatedConvolution2D(4, 10, ksize=3, stride=1, pad=1, dilate=1)

    vx = chainer.Variable(np.random.rand(2, 4, 6, 8).astype(np.float32))
    vy = link(vx)

    graph = ChainerConverter().convert_from_inout_vars([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] L.DilatedConvolution2D(dilate=1)",
        graph=graph,
        inputs={x: ConstantVariable(vx.data, OrderNCHW).change_order(x.order).data},
        expected={y: ConstantVariable(vy.data, OrderNCHW).change_order(y.order).data}
    )


def test_dilate_is_2():
    link = chainer.links.DilatedConvolution2D(4, 10, ksize=3, stride=1, pad=1, dilate=2)

    vx = chainer.Variable(np.random.rand(2, 4, 6, 8).astype(np.float32))
    vy = link(vx)

    graph = ChainerConverter().convert_from_inout_vars([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] L.DilatedConvolution2D(dilate=2)",
        graph=graph,
        inputs={x: ConstantVariable(vx.data, OrderNCHW).change_order(x.order).data},
        expected={y: ConstantVariable(vy.data, OrderNCHW).change_order(y.order).data}
    )


def test_nobias():
    link = chainer.links.DilatedConvolution2D(4, 10, ksize=3, stride=1, pad=1, dilate=2, nobias=True)

    vx = chainer.Variable(np.random.rand(2, 4, 6, 8).astype(np.float32))
    vy = link(vx)

    graph = ChainerConverter().convert_from_inout_vars([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] L.DilatedConvolution2D(dilate=2, nobias=True)",
        graph=graph,
        inputs={x: ConstantVariable(vx.data, OrderNCHW).change_order(x.order).data},
        expected={y: ConstantVariable(vy.data, OrderNCHW).change_order(y.order).data}
    )
