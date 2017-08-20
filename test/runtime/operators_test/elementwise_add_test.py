import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn.graph.graph import Graph
from webdnn.graph.order import OrderNHWC, OrderNCHW, OrderC
from webdnn.graph.variable import Variable


@wrap_template
def template(shape=(2, 3, 4, 5), x1_order=OrderNHWC, x2_order=OrderNHWC, y_order=OrderNHWC,
             description: str = ""):
    # vx1 = np.random.rand(*shape).astype(np.float32) - 0.5
    # vx2 = np.random.rand(*shape).astype(np.float32) - 0.5
    vx1 = np.arange(np.prod(shape)).reshape(shape).astype(np.float32)
    vx2 = np.arange(np.prod(shape)).reshape(shape).astype(np.float32)
    vy = vx1 + vx2

    x1 = Variable(vx1.shape, order=OrderNHWC)
    x2 = Variable(vx2.shape, order=OrderNHWC)
    y = x1 + x2
    x1.change_order(x1_order)
    x2.change_order(x2_order)
    y.change_order(y_order)

    generate_kernel_test_case(
        description=f"ElementwiseAdd {description}",
        graph=Graph([x1, x2], [y]),
        inputs={
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
    vx1 = np.random.rand(3)
    vx2 = np.random.rand(2, 3, 4, 5) - 0.5
    vy = vx1[None, :, None, None] + vx2

    x1 = Variable(vx1.shape, order=OrderC)
    x2 = Variable(vx2.shape, order=OrderNCHW)
    y = x1 + x2
    y.change_order(OrderNCHW)

    generate_kernel_test_case(
        description=f"ElementwiseAdd broadcast",
        graph=Graph([x1, x2], [y]),
        inputs={x1: vx1, x2: vx2},
        expected={y: vy},
    )
