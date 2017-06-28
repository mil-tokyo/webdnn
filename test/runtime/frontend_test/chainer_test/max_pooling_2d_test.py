import chainer
import numpy as np

from test.util import generate_kernel_test_case
from webdnn.frontend.chainer import ChainerConverter
from webdnn.graph.order import OrderNCHW
from webdnn.graph.variables.constant_variable import ConstantVariable


def test():
    vx = chainer.Variable(np.random.rand(2, 4, 6, 8))
    vy = chainer.functions.max_pooling_2d(vx, ksize=2, stride=2)

    graph = ChainerConverter().convert_from_inout_vars([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] F.average_pooling_2d(ksize=2, stride=2, padding=0)",
        graph=graph,
        inputs={x: ConstantVariable(vx.data, OrderNCHW).change_order(x.order).data},
        expected={y: ConstantVariable(vy.data, OrderNCHW).change_order(y.order).data}
    )


def test_padding_not_zero():
    vx = chainer.Variable(np.random.rand(2, 4, 6, 8))
    vy = chainer.functions.max_pooling_2d(vx, ksize=2, stride=2, pad=1)

    graph = ChainerConverter().convert_from_inout_vars([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] F.average_pooling_2d(ksize=2, stride=2, padding=1)",
        graph=graph,
        inputs={x: ConstantVariable(vx.data, OrderNCHW).change_order(x.order).data},
        expected={y: ConstantVariable(vy.data, OrderNCHW).change_order(y.order).data}
    )


def test_stride_is_none():
    vx = chainer.Variable(np.random.rand(2, 4, 6, 8))
    vy = chainer.functions.max_pooling_2d(vx, ksize=2, stride=None, pad=1)

    graph = ChainerConverter().convert_from_inout_vars([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] F.average_pooling_2d(ksize=2, stride=None(=ksize), padding=1)",
        graph=graph,
        inputs={x: ConstantVariable(vx.data, OrderNCHW).change_order(x.order).data},
        expected={y: ConstantVariable(vy.data, OrderNCHW).change_order(y.order).data}
    )


def test_irregular_size():
    vx = chainer.Variable(np.random.rand(2, 4, 6, 8))
    vy = chainer.functions.max_pooling_2d(vx, ksize=(3, 4), stride=(1, 2), pad=(1, 3))

    graph = ChainerConverter().convert_from_inout_vars([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] F.max_pooling_2d(ksize=(3,4), stride=(1,2), padding=(1,3))",
        graph=graph,
        inputs={x: ConstantVariable(vx.data, OrderNCHW).change_order(x.order).data},
        expected={y: ConstantVariable(vy.data, OrderNCHW).change_order(y.order).data}
    )
