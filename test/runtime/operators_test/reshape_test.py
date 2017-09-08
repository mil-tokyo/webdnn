import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn.graph.graph import Graph
from webdnn.graph.operators.reshape import Reshape
from webdnn.graph.order import OrderNHWC
from webdnn.graph.variable import Variable


@wrap_template
def template(x_order=OrderNHWC, x_shape=(2, 3, 4, 5), y_order=OrderNHWC, y_shape=(1, 12, 2, 5), description: str = ""):
    vx = np.random.rand(*x_shape) - 0.5

    x = Variable(vx.shape, order=OrderNHWC)
    y, = Reshape(None, in_order=x_order, out_order=y_order, out_shape=y_shape)(x)

    x.change_order(x_order)
    y.change_order(y_order)

    generate_kernel_test_case(
        description=f"Reshape {description}",
        graph=Graph([x], [y]),
        inputs={x: np.transpose(vx, [OrderNHWC.axes_dict[a] for a in x.order.axes]).flatten()},
        expected={y: np.transpose(vx, [OrderNHWC.axes_dict[a] for a in y.order.axes]).flatten()},
    )


def test():
    template()
