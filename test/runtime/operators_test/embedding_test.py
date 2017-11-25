import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.operators.embedding import Embedding
from webdnn.graph.order import OrderNT, OrderCN, OrderNTC, Order
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable


@wrap_template
def template(x_shape=[2, 3], feature_size=5, vocabulary_size=6, x_order=OrderNT, w_order=OrderCN, y_order=OrderNTC, description: str = ""):
    x = Variable(x_shape, order=x_order)

    vx = np.random.randint(low=0, high=vocabulary_size, size=(x.shape_dict[Axis.N], x.shape_dict[Axis.T]))  # OrderNT
    vw = np.random.rand(vocabulary_size, feature_size)  # OrderCN
    vy = vw[vx]  # OrderNTC

    w = ConstantVariable(vw, order=OrderCN)
    y, = Embedding(None)(x, w)

    x = x.change_order(x_order)
    w = w.change_order(w_order)
    y = y.change_order(y_order)

    generate_kernel_test_case(
        description=f"Embedding {description}",
        backend=["webgpu", "webassembly"],
        graph=Graph([x], [y]),
        inputs={x: vx.transpose([OrderNT.axes_dict[a] for a in x.order.axes])},
        expected={y: vy.transpose([OrderNTC.axes_dict[a] for a in y.order.axes])}
    )


def test():
    template()


def test_X_TN():
    template(x_order=Order([Axis.T, Axis.N]))


def test_W_NC():
    template(w_order=Order([Axis.N, Axis.C]))


def test_Y_CTN():
    template(w_order=Order([Axis.C, Axis.T, Axis.N]))
