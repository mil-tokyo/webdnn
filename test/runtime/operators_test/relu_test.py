import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn.graph.graph import Graph
from webdnn.graph.operators.relu import Relu
from webdnn.graph.order import OrderNHWC, OrderNCHW
from webdnn.graph.variable import Variable


@wrap_template
def template(x_order=OrderNHWC, x_shape=(2, 3, 4, 5), y_order=OrderNHWC, description: str = ""):
    vx = np.random.rand(*x_shape) - 0.5
    vy = vx * (vx > 0)

    x = Variable(vx.shape, order=x_order)
    y, = Relu(None)(x)
    y.change_order(y_order)

    generate_kernel_test_case(
        description=f"Relu {description}",
        graph=Graph([x], [y]),
        inputs={x: vx},
        expected={y: np.transpose(vy, [x_order.axes_dict[a] for a in y_order.axes])},
    )


def test():
    template()


def test_different_order():
    template(x_order=OrderNCHW)
