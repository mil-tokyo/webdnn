import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn.graph.graph import Graph
from webdnn.graph.operators.sin import Sin
from webdnn.graph.order import OrderNHWC, OrderNCHW
from webdnn.graph.variable import Variable


@wrap_template
def template(r=1.0, x_shape=[2, 3, 4, 5], x_order=OrderNHWC, y_order=OrderNHWC, description: str = ""):
    vx = (np.random.rand(*x_shape) - 0.5) * r
    vy = np.sin(vx)

    x = Variable(vx.shape, order=x_order)
    y, = Sin(None)(x)

    y.change_order(y_order)

    generate_kernel_test_case(
        description=f"Sin {description}",
        graph=Graph([x], [y]),
        inputs={x: vx},
        expected={y: np.transpose(vy, [x_order.axes_dict[a] for a in y_order.axes])},
        EPS=1e-2
    )


def test():
    template()


def test_different_order():
    template(x_order=OrderNCHW)
