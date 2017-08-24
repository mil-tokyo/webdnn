import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn.graph.graph import Graph
from webdnn.graph.operators.clipped_relu import ClippedRelu
from webdnn.graph.order import OrderNHWC, OrderNCHW
from webdnn.graph.variable import Variable


@wrap_template
def template(x_order=OrderNHWC, y_order=OrderNHWC, cap=0.25, description: str = ""):
    vx = np.random.rand(2, 3, 4, 5) - 0.5
    vy = np.clip(vx, 0.0, cap)

    x = Variable(vx.shape, order=OrderNHWC)
    y, = ClippedRelu(None, cap=cap)(x)

    y.change_order(x_order)
    y.change_order(y_order)

    generate_kernel_test_case(
        description=f"ClippedRelu {description}",
        graph=Graph([x], [y]),
        inputs={x: np.transpose(vx, [OrderNHWC.axes_dict[a] for a in x.order.axes])},
        expected={y: np.transpose(vy, [OrderNHWC.axes_dict[a] for a in y.order.axes])},
    )


def test():
    template()


def test_different_order():
    template(x_order=OrderNCHW)


def test_cap_1():
    template(cap=1)


def test_cap_0():
    template(cap=0)
