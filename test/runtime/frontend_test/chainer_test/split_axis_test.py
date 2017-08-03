import chainer
import numpy as np

from test.util import generate_kernel_test_case
from webdnn.frontend.chainer.converter import ChainerConverter
from webdnn.graph.order import OrderNCHW


def test():
    vx = chainer.Variable(np.random.rand(2, 8, 6, 12))
    vy1, vy2, vy3 = chainer.functions.split_axis(vx, [4, 10], 3)

    graph = ChainerConverter().convert_from_inout_vars([vx], [vy1, vy2, vy3])

    x = graph.inputs[0]
    y1 = graph.outputs[0]
    y2 = graph.outputs[1]
    y3 = graph.outputs[2]

    generate_kernel_test_case(
        description=f"[chainer] F.SplitAxis",
        graph=graph,
        inputs={x: np.transpose(vx.data, [OrderNCHW.axes_dict[a] for a in x.order.axes])},
        expected={
            y1: np.transpose(vy1.data, [OrderNCHW.axes_dict[a] for a in y1.order.axes]),
            y2: np.transpose(vy2.data, [OrderNCHW.axes_dict[a] for a in y2.order.axes]),
            y3: np.transpose(vy3.data, [OrderNCHW.axes_dict[a] for a in y3.order.axes])
        },
    )
