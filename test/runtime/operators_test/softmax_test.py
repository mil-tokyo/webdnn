import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.operators.softmax import Softmax
from webdnn.graph.order import OrderNC, OrderCN, OrderNCHW
from webdnn.graph.variable import Variable


@wrap_template
def template(x_order=OrderNC, y_order=OrderNC, axis=Axis.C, description: str = ""):
    shape = (np.arange(x_order.ndim) + 2).tolist()
    vx = np.random.rand(*shape) - 0.5
    vy = np.exp(vx) / np.sum(np.exp(vx), axis=x_order.axes_dict[axis], keepdims=True)

    x = Variable(vx.shape, order=x_order)
    y, = Softmax(None, axis=axis)(x)

    y.change_order(y_order)

    generate_kernel_test_case(
        description=f"Softmax {description}",
        graph=Graph([x], [y]),
        inputs={x: vx},
        backend=["webgpu", "webassembly"],
        expected={y: np.transpose(vy, [x_order.axes_dict[a] for a in y.order.axes])},
    )


def test():
    template()


def test_different_order():
    template(x_order=OrderCN)


def test_axis_first_axis():
    template(axis=Axis.N)


def test_4d_first_axis():
    template(x_order=OrderNCHW, y_order=OrderNCHW, axis=Axis.N)


def test_4d_middle_axis():
    template(x_order=OrderNCHW, y_order=OrderNCHW, axis=Axis.C)


def test_4d_last_axis():
    template(x_order=OrderNCHW, y_order=OrderNCHW, axis=Axis.W)
