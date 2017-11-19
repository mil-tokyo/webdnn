import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn.graph.graph import Graph
from webdnn.graph.order import OrderNHWC, OrderNCHW
from webdnn.graph.variable import Variable


@wrap_template
def template(x_order=OrderNHWC, y_order=OrderNCHW, description: str = ""):
    vx = np.random.rand(2, 3, 4, 5)
    vy = np.transpose(vx, [x_order.axes_dict[a] for a in y_order.axes])

    x = Variable(vx.shape, order=x_order)
    y = x.transpose(y_order)

    generate_kernel_test_case(
        description=f"Transpose {description}",
        backend=["webgpu", "webgl", "webassembly"],
        graph=Graph([x], [y]),
        inputs={x: vx},
        expected={y: vy},
    )


def test():
    template()


def test_no_change():
    template(x_order=OrderNHWC, y_order=OrderNHWC)
