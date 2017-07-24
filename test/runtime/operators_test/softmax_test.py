import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.operators.softmax import Softmax
from webdnn.graph.order import OrderNC, OrderCN
from webdnn.graph.variable import Variable


@wrap_template
def template(x_order=OrderNC, y_order=OrderNC, axis=Axis.C, description: str = ""):
    vx = np.random.rand(2, 3) - 0.5
    vy = np.exp(vx) / np.sum(np.exp(vx), axis=OrderNC.axes_dict[axis], keepdims=True)

    x = Variable(vx.shape, order=OrderNC)
    y, = Softmax(None, axis=axis)(x)

    x.change_order(x_order)
    y.change_order(y_order)

    generate_kernel_test_case(
        description=f"Softmax {description}",
        graph=Graph([x], [y]),
        inputs={x: np.transpose(vx, [OrderNC.axes_dict[a] for a in x.order.axes])},
        expected={y: np.transpose(vy, [OrderNC.axes_dict[a] for a in y.order.axes])},
    )


def test():
    template()

# FIXME: Not supported yet
# def test_different_order():
#     template(x_order=OrderCN)
