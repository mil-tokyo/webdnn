import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn.graph.graph import Graph
from webdnn.graph.operators.asin import Asin
from webdnn.graph.order import OrderNHWC, OrderNCHW
from webdnn.graph.variable import Variable


@wrap_template
def template(x_shape=[2, 3, 4, 5], x_order=OrderNHWC, y_order=OrderNHWC, description: str = ""):
    vx = np.random.rand(*x_shape) * 2 - 1  # domain: [-1, 1]
    vy = np.arcsin(vx)

    x = Variable(vx.shape, order=x_order)
    y, = Asin(None)(x)

    y.change_order(y_order)

    generate_kernel_test_case(
        description=f"Asin {description}",
        graph=Graph([x], [y]),
        inputs={x: vx},
        expected={y: np.transpose(vy, [x_order.axes_dict[a] for a in y_order.axes])},
        EPS=1e-2
    )


def test():
    template()


def test_different_order():
    template(x_order=OrderNCHW)
