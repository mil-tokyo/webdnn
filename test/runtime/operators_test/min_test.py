import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.operators.min import Min
from webdnn.graph.order import OrderNHWC, OrderNCHW, OrderC
from webdnn.graph.variable import Variable


@wrap_template
def template(x_shape=[2, 3, 4, 5], x_order=OrderNHWC, y_order=OrderNHWC, axis=Axis.C, description: str = ""):
    vx = np.random.rand(*x_shape)
    vy = np.min(vx, axis=x_order.axes_dict[axis], keepdims=True)

    x = Variable(vx.shape, order=x_order)
    y, = Min(None, axis=axis)(x)

    y.change_order(y_order)

    generate_kernel_test_case(
        description=f"Min {description}",
        graph=Graph([x], [y]),
        backend=["webgpu", "webgl", "webassembly"],
        inputs={x: vx},
        expected={y: np.transpose(vy, [x.order.axes_dict[a] for a in y.order.axes])},
    )


def test():
    template()


def test_different_order():
    template(x_order=OrderNCHW)


def test_reduced_to_scalar():
    template(x_shape=[10], x_order=OrderC, y_order=OrderC)
