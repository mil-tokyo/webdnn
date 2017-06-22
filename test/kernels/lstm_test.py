import numpy as np
from chainer import Variable
from chainer.functions.activation.lstm import lstm
from chainer.functions.connection.linear import linear

from test.util import generate_kernel_test_case
from webdnn.graph.graph import Graph
from webdnn.graph.operators.lstm import LSTM
from webdnn.graph.order import OrderNTC, OrderCN, OrderC
from webdnn.graph.variable import Variable


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
    w_input = Variable(vw_input.shape, order=OrderCN)
    w_hidden = Variable(vw_hidden.shape, order=OrderCN)
    b = Variable(vb.shape, order=OrderC)
    y, = LSTM(None)(x, w_input, w_hidden, b)

    generate_kernel_test_case(
        description=f"LSTM",
        backend=["webgpu"],
        graph=Graph([x, w_input, w_hidden, b], [y]),
        inputs={
            x: vx,
            w_input: vw_input,
            w_hidden: vw_hidden,
            b: vb
        },
        expected={y: vy}
    )
