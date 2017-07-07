import chainer
import numpy as np

from test.util import generate_kernel_test_case
from webdnn.frontend.chainer.converter import ChainerConverter
from webdnn.graph.order import OrderNCHW
from webdnn.graph.variables.constant_variable import ConstantVariable


def test():
    vx1 = chainer.Variable(np.random.rand(2, 4, 6, 8))
    vx2 = chainer.Variable(np.random.rand(2, 4, 6, 8))
    vy = vx1 * vx2

    graph = ChainerConverter().convert_from_inout_vars([vx1, vx2], [vy])

    x1 = graph.inputs[0]
    x2 = graph.inputs[1]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] F.Mul",
        graph=graph,
        inputs={
            x1: ConstantVariable(vx1.data, OrderNCHW).change_order(x1.order).data,
            x2: ConstantVariable(vx2.data, OrderNCHW).change_order(x2.order).data
        },
        expected={y: ConstantVariable(vy.data, OrderNCHW).change_order(y.order).data}
    )


def test_add_itself():
    vx = chainer.Variable(np.random.rand(2, 4, 6, 8))
    vy = vx * vx

    graph = ChainerConverter().convert_from_inout_vars([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] F.Mul (y=x*x)",
        graph=graph,
        inputs={x: ConstantVariable(vx.data, OrderNCHW).change_order(x.order).data},
        expected={y: ConstantVariable(vy.data, OrderNCHW).change_order(y.order).data}
    )
