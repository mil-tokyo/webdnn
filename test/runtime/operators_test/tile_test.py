import numpy as np
from webdnn.graph.axis import AxisKeyDict
from webdnn.graph.graph import Graph
from webdnn.graph.operators.tile import Tile
from webdnn.graph.order import OrderNHWC, OrderNCHW
from webdnn.graph.variable import Variable

from test.util import generate_kernel_test_case, wrap_template


@wrap_template
def template(x_order=OrderNHWC, x_shape=[2, 3, 4, 5],
             multiplier=AxisKeyDict(OrderNHWC.axes, [3, 4, 5, 6]),
             y_order=OrderNHWC, description: str = ""):
    vx = np.random.rand(*x_shape)
    vy = np.tile(vx, [multiplier[a] for a in x_order.axes])

    x = Variable(vx.shape, order=x_order)
    y, = Tile(None, multiplier=multiplier)(x)

    y.change_order(y_order)

    generate_kernel_test_case(
        description=f"Tile {description}",
        graph=Graph([x], [y]),
        backend=["webgpu", "webassembly", "webgl"],
        inputs={x: vx},
        expected={y: np.transpose(vy.data, [x_order.axes_dict[a] for a in y.order.axes])},
        EPS=1e-2
    )


def test():
    template()


def test_different_order():
    template(x_order=OrderNCHW)
