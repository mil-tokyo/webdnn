import chainer
import numpy as np

from test.util import generate_kernel_test_case
from webdnn.frontend.chainer.converter import ChainerConverter
from webdnn.graph.order import OrderNCHW


def test():
    vx1 = chainer.Variable(np.random.rand(2, 4, 6, 8))
    vx2 = chainer.Variable(np.random.rand(2, 4, 6, 8))
    vy = vx1 / vx2

    graph = ChainerConverter().convert_from_inout_vars([vx1, vx2], [vy])

    x1 = graph.inputs[0]
    x2 = graph.inputs[1]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] F.Div",
        graph=graph,
        inputs={
            x1: np.transpose(vx1.data, [OrderNCHW.axes_dict[a] for a in x1.order.axes]),
            x2: np.transpose(vx2.data, [OrderNCHW.axes_dict[a] for a in x2.order.axes])
        },
        expected={y: np.transpose(vy.data, [OrderNCHW.axes_dict[a] for a in y.order.axes])},
    )


def test_itself():
    vx = chainer.Variable(np.random.rand(2, 4, 6, 8))
    vy = vx / vx

    graph = ChainerConverter().convert_from_inout_vars([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] F.Div itself",
        graph=graph,
        inputs={x: np.transpose(vx.data, [OrderNCHW.axes_dict[a] for a in x.order.axes])},
        expected={y: np.transpose(vy.data, [OrderNCHW.axes_dict[a] for a in y.order.axes])},
    )
