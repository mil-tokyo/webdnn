import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.operators.prod import Prod
from webdnn.graph.order import OrderNHWC, OrderNCHW, Order
from webdnn.graph.variable import Variable

OrderNHW = Order([Axis.N, Axis.H, Axis.W])


@wrap_template
def template(x_order=OrderNHWC, y_order=OrderNHW, axis=Axis.C, description: str = ""):
    vx = np.arange(120).reshape(2, 3, 4, 5)
    vy = np.prod(vx, axis=OrderNHWC.axes_dict[axis])

    x = Variable(vx.shape, order=OrderNHWC)
    y, = Prod(None, axis=axis)(x)

    x.change_order(x_order)
    y.change_order(y_order)

    generate_kernel_test_case(
        description=f"Prod {description}",
        graph=Graph([x], [y]),
        backend=["webgpu", "webgl", "webassembly"],
        inputs={x: np.transpose(vx, [OrderNHWC.axes_dict[a] for a in x.order.axes])},
        expected={y: np.transpose(vy, [OrderNHW.axes_dict[a] for a in y.order.axes])},
    )


def test():
    template()


def test_different_order():
    template(x_order=OrderNCHW)
