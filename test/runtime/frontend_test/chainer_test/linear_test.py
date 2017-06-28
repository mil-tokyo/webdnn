import chainer
import numpy as np

from test.util import generate_kernel_test_case
from webdnn.frontend.chainer import ChainerConverter
from webdnn.graph.order import OrderNCHW, OrderNC
from webdnn.graph.variables.constant_variable import ConstantVariable


def test_2d():
    link = chainer.links.Linear(4, 10)

    vx = chainer.Variable(np.random.rand(2, 4).astype(np.float32))
    vy = link(vx)

    graph = ChainerConverter().convert_from_inout_vars([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] L.Linear(input is 2D tensor)",
        graph=graph,
        inputs={x: ConstantVariable(vx.data, OrderNC).change_order(x.order).data},
        expected={y: ConstantVariable(vy.data, OrderNC).change_order(y.order).data}
    )


def test_4d():
    link = chainer.links.Linear(4 * 6 * 8, 10)

    vx = chainer.Variable(np.random.rand(2, 4, 6, 8).astype(np.float32))
    vy = link(vx)

    graph = ChainerConverter().convert_from_inout_vars([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] L.Linear(input is 4D tensor)",
        graph=graph,
        inputs={x: ConstantVariable(vx.data, OrderNCHW).change_order(x.order).data},
        expected={y: ConstantVariable(vy.data, OrderNC).change_order(y.order).data}
    )


def test_nobias():
    link = chainer.links.Linear(4 * 6 * 8, 10, nobias=True)

    vx = chainer.Variable(np.random.rand(2, 4, 6, 8).astype(np.float32))
    vy = link(vx)

    graph = ChainerConverter().convert_from_inout_vars([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] L.Linear(nobias=True)",
        graph=graph,
        inputs={x: ConstantVariable(vx.data, OrderNCHW).change_order(x.order).data},
        expected={y: ConstantVariable(vy.data, OrderNC).change_order(y.order).data}
    )
