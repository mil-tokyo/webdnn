import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn.graph.graph import Graph
from webdnn.graph.operators.threshold_relu import ThresholdRelu
from webdnn.graph.order import OrderNHWC, OrderNCHW
from webdnn.graph.variable import Variable


@wrap_template
def template(x_order=OrderNHWC, y_order=OrderNHWC, threshold=0.5, description: str = ""):
    vx = np.random.rand(2, 3, 4, 5) - 0.5
    vy = vx * (vx > threshold)

    x = Variable(vx.shape, order=OrderNHWC)
    y, = ThresholdRelu(None, threshold=threshold)(x)

    x.change_order(x_order)
    y.change_order(y_order)

    generate_kernel_test_case(
        description=f"ThresholdRelu {description}",
        graph=Graph([x], [y]),
        inputs={x: np.transpose(vx, [OrderNHWC.axes_dict[a] for a in x.order.axes])},
        expected={y: np.transpose(vy, [OrderNHWC.axes_dict[a] for a in y.order.axes])},
    )


def test():
    template()


def test_different_order():
    template(x_order=OrderNCHW)


def test_threshold():
    template(threshold=0.2)


def test_threshold_zero():
    template(threshold=0)
