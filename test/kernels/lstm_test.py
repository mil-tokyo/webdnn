import numpy as np
from chainer import Variable
from chainer.functions.activation.lstm import lstm
from chainer.functions.connection.linear import linear

from test.util import generate_kernel_test_case
from webdnn.graph.graph import Graph
from webdnn.graph.operators.lstm import LSTM
from webdnn.graph.order import OrderNTC, OrderCN, OrderC
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable


def test_general():
    N = 1
    T = 80
    C1 = 128
    C2 = 128
    vx = np.random.normal(size=(N, T, C1))
    vw_input = np.random.normal(size=(C1, C2 * 4))
    vw_hidden = np.random.normal(size=(C2, C2 * 4))
    vb = np.random.normal(size=(C2 * 4))
    vc = np.zeros((N, C2))
    vy = np.zeros((N, C2))

    for i in range(T - 1):
        vc, vy = lstm(vc, linear(vx[:, i, :], vw_input.T) + linear(vy, vw_hidden.T, vb))
    _, vy = lstm(vc, linear(vx[:, T - 1, :], vw_input.T) + linear(vy, vw_hidden.T, vb))

    vy = vy.data

    x = Variable(vx.shape, order=OrderNTC)
    w_input = ConstantVariable(vw_input, order=OrderCN)
    w_hidden = ConstantVariable(vw_hidden, order=OrderCN)
    b = ConstantVariable(vb, order=OrderC)
    y, = LSTM(None)(x, w_input, w_hidden, b)

    generate_kernel_test_case(
        description=f"LSTM",
        backend=["webgpu", "webassembly"],
        graph=Graph([x], [y]),
        inputs={x: vx},
        expected={y: vy}
    )
