import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn.graph.graph import Graph
from webdnn.graph.operators.sigmoid import Sigmoid
from webdnn.graph.order import OrderCNHW, OrderNHWC
from webdnn.graph.variable import Variable


@wrap_template
def template(r=1.0, x_order=OrderNHWC, y_order=OrderNHWC, description: str = ""):
    vx = (np.random.rand(2, 3, 4, 5) - 0.5) * r
    vy = 1 / (1 + np.exp(-vx))
    # This produces very small positive value (< 1e-7) when vx is negative large.
    # Actual implementation uses tanh(0.5f * x0) * 0.5f + 0.5f
    # In the case tanh is used, the result saturates to 0.0 when vs is negative large.
    # ABS_EPS is set to allow such case.

    x = Variable(vx.shape, order=OrderNHWC)
    y, = Sigmoid(None)(x)

    x.change_order(x_order)
    y.change_order(y_order)

    generate_kernel_test_case(
        description=f"Sigmoid {description}",
        graph=Graph([x], [y]),
        inputs={x: np.transpose(vx, [OrderNHWC.axes_dict[a] for a in x.order.axes])},
        expected={y: np.transpose(vy, [OrderNHWC.axes_dict[a] for a in y.order.axes])},
        ABS_EPS=1e-7
    )


def test():
    template()


def test_different_order():
    template(x_order=OrderCNHW)


def test_large_range():
    template(r=1e3)
