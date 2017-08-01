import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn.graph.graph import Graph
from webdnn.graph.operators.broadcast import Broadcast
from webdnn.graph.order import OrderNHWC, OrderNCHW
from webdnn.graph.variable import Variable


@wrap_template
def template(x_order=OrderNHWC, y_order=OrderNHWC, out_shape=None, description: str = ""):
    if out_shape is None:
        out_shape = [2, 3, 4, 5]

    vx = np.random.rand(2, 1, 1, 5)
    vy = np.broadcast_to(vx, out_shape)

    x = Variable(vx.shape, order=OrderNHWC)
    y, = Broadcast(None, out_shape=out_shape, out_order=x.order)(x)

    x.change_order(x_order)
    y.change_order(y_order)

    generate_kernel_test_case(
        description=f"Broadcast {description}",
        graph=Graph([x], [y]),
        inputs={x: np.transpose(vx, [OrderNHWC.axes_dict[a] for a in x.order.axes])},
        expected={y: np.transpose(vy, [OrderNHWC.axes_dict[a] for a in y.order.axes])},
    )


def test():
    template()


def test_different_order():
    template(x_order=OrderNCHW)
