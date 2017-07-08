import chainer
import numpy as np

from test.util import generate_kernel_test_case
from webdnn.frontend.chainer.converter import ChainerConverter
from webdnn.graph.order import OrderNCHW
from webdnn.graph.variables.constant_variable import ConstantVariable


def test_var_var():
    vx1 = chainer.Variable(np.random.rand(2, 4, 6, 8))
    vx2 = chainer.Variable(np.random.rand(2, 4, 6, 8))
    vy = vx1 ** vx2

    graph = ChainerConverter().convert_from_inout_vars([vx1, vx2], [vy])

    x1 = graph.inputs[0]
    x2 = graph.inputs[1]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] F.PowVarVar",
        graph=graph,
        inputs={
            x1: ConstantVariable(vx1.data, OrderNCHW).change_order(x1.order).data,
            x2: ConstantVariable(vx2.data, OrderNCHW).change_order(x2.order).data
        },
        expected={y: ConstantVariable(vy.data, OrderNCHW).change_order(y.order).data}
    )
