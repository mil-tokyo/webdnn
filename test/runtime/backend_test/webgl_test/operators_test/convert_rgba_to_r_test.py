import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn.backend.webgl.operators.convert_rgba_to_r import ConvertRGBAtoR
from webdnn.graph.graph import Graph
from webdnn.graph.order import OrderNHWC, OrderNCHW, Order
from webdnn.graph.variable import Variable


@wrap_template
def template(x_shape=(2, 3, 4, 5), x_order: Order = OrderNHWC, y_order: Order = OrderNHWC, description: str = ""):
    vx = np.arange(np.product(x_shape)).reshape(x_shape)
    vy = vx.copy()

    x = Variable(vx.shape, order=x_order)
    y, = ConvertRGBAtoR(None)(x)

    y.change_order(y_order)

    generate_kernel_test_case(
        description=f"ConvertRGBAtoR {description}",
        graph=Graph([x], [y]),
        backend=["webgl"],
        inputs={x: vx},
        expected={y: np.transpose(vy, [x_order.axes_dict[a] for a in y.order.axes])},
    )


def test():
    template()


def test_change_order():
    template(x_order=OrderNHWC, y_order=OrderNCHW)
