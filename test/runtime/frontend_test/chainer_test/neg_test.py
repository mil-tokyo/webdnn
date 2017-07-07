import chainer
import numpy as np

from test.util import generate_kernel_test_case
from webdnn.frontend.chainer.converter import ChainerConverter
from webdnn.graph.order import OrderNC
from webdnn.graph.variables.constant_variable import ConstantVariable


def test():
    vx = chainer.Variable(np.random.rand(6, 8))
    vy = -vx

    graph = ChainerConverter().convert_from_inout_vars([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] F.Neg",
        graph=graph,
        inputs={x: ConstantVariable(vx.data, OrderNC).change_order(x.order).data},
        expected={y: ConstantVariable(vy.data, OrderNC).change_order(y.order).data}
    )
