import numpy as np
from webdnn.graph.graph import Graph
from webdnn.graph.order import OrderNHWC, OrderNCHW, OrderCNHW
from webdnn.graph.variable import Variable

from test.util import generate_kernel_test_case, wrap_template


@wrap_template
def template(x_order=OrderNHWC, x_shape=(2, 3, 4, 5), actual_x_order=OrderNHWC,
             y_order=OrderNHWC, y_shape=(1, 12, 2, 5), actual_y_order=OrderNHWC, description: str = ""):
    vx = np.arange(np.product(x_shape)).reshape(x_shape)
    vy = vx.reshape(y_shape)

    x = Variable(vx.shape, order=x_order)
    y = x.reshape(shape=y_shape, order=y_order)

    x.change_order(actual_x_order)
    y.change_order(actual_y_order)

    generate_kernel_test_case(
        description=f"Reshape {description}",
        backend=["webgpu", "webgl", "webassembly"],
        graph=Graph([x], [y]),
        inputs={x: vx.transpose([x_order.axes_dict[a] for a in actual_x_order.axes])},
        expected={y: vy.transpose([y_order.axes_dict[a] for a in actual_y_order.axes])},
    )


def test():
    template()


def test_different_order():
    template(actual_x_order=OrderNCHW, actual_y_order=OrderCNHW)
