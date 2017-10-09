import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn.backend.webgl.operators.convert_r_to_rgba import ConvertRtoRGBA
from webdnn.graph.graph import Graph
from webdnn.graph.order import OrderNHWC, OrderNCHW, Order
from webdnn.graph.variable import Variable


@wrap_template
def template(x_shape=(2, 3, 4, 5), x_order: Order = OrderNHWC, y_order: Order = OrderNHWC, description: str = ""):
    vx = np.random.rand(*x_shape) - 0.5
    vy = vx.copy()

    x = Variable(vx.shape, order=OrderNHWC)
    y, = ConvertRtoRGBA(None)(x)

    x.change_order(x_order)
    y.change_order(y_order)

    generate_kernel_test_case(
        description=f"ConvertRtoRGBA {description}",
        graph=Graph([x], [y]),
        backend=["webgl"],
        inputs={x: np.transpose(vx, [OrderNHWC.axes_dict[a] for a in x.order.axes])},
        expected={y: np.transpose(vy, [OrderNHWC.axes_dict[a] for a in y.order.axes])},
    )


def test():
    template()


def test_change_order():
    template(x_order=OrderNHWC, y_order=OrderNCHW)
