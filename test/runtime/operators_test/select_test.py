import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.operators.select import Select
from webdnn.graph.order import OrderNHWC, OrderNCHW, OrderNC, Order
from webdnn.graph.variable import Variable


@wrap_template
def template(shape=(2, 3, 4, 5), x0_order=OrderNHWC, x1_order=OrderNHWC, x2_order=OrderNHWC, y_order=OrderNHWC, description: str = ""):
    vx0 = np.where(np.random.rand(*shape).astype(np.float32) > 0.5, 0, 1)
    vx1 = np.random.rand(*shape).astype(np.float32) - 0.5
    vx2 = np.random.rand(*shape).astype(np.float32) - 0.5
    vy = np.where(vx0 == 1, vx1, vx2)

    x0 = Variable(vx0.shape, order=OrderNHWC)
    x1 = Variable(vx1.shape, order=OrderNHWC)
    x2 = Variable(vx2.shape, order=OrderNHWC)
    y, = Select(None)(x0, x1, x2)
    x0.change_order(x0_order)
    x1.change_order(x1_order)
    x2.change_order(x2_order)
    y.change_order(y_order)

    generate_kernel_test_case(
        description=f"Select {description}",
        graph=Graph([x0, x1, x2], [y]),
        inputs={
            x0: np.transpose(vx0, [OrderNHWC.axes_dict[a] for a in x0.order.axes]),
            x1: np.transpose(vx1, [OrderNHWC.axes_dict[a] for a in x1.order.axes]),
            x2: np.transpose(vx2, [OrderNHWC.axes_dict[a] for a in x2.order.axes])
        },
        expected={y: np.transpose(vy, [OrderNHWC.axes_dict[a] for a in y.order.axes])},
    )


def test():
    template()


def test_large():
    template(shape=(2, 3, 4, 2047))


def test_different_order():
    template(x1_order=OrderNCHW)


def test_broadcast():
    vx0 = np.where(np.random.rand(*[2, 5]).astype(np.float32) > 0.5, 0, 1)
    vx1 = np.random.rand(*[3, 4]).astype(np.float32) - 0.5
    vx2 = np.random.rand(*[2, 3, 4, 5]).astype(np.float32) - 0.5
    vy = np.where(vx0[:, None, None, :] == 1, vx1[None, :, :, None], vx2)

    x0 = Variable(vx0.shape, order=OrderNC)
    x1 = Variable(vx1.shape, order=Order([Axis.H, Axis.W]))
    x2 = Variable(vx2.shape, order=OrderNHWC)
    y, = Select(None)(x0, x1, x2)
    y.change_order(OrderNHWC)

    generate_kernel_test_case(
        description=f"Select broadcast",
        graph=Graph([x0, x1, x2], [y]),
        inputs={x0: vx0, x1: vx1, x2: vx2},
        expected={y: vy},
    )
