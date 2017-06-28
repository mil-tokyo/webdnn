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


def _convert_to_chainer_order(x):
    # NOTE:
    # In WebDNN, W_i, W_h, and b contains weights about input gate(v_i), forget gate(v_f) activated value(v_a), and output gate(v_o).
    # However in chainer, they are packed as the order of v_a, v_i, v_f, and v_o
    return x.reshape(x.shape[0], 4, x.shape[1] // 4).swapaxes(1, 2)[:, :, [2, 0, 1, 3]].reshape(x.shape)


def test_t_is_1():
    N = 1
    T = 1
    C1 = 128
    C2 = 64
    vx = np.random.normal(size=(N, T, C1))
    vw_input = np.random.normal(size=(C1, C2 * 4))
    vw_hidden = np.random.normal(size=(C2, C2 * 4))
    vb = np.random.normal(size=(C2 * 4,))
    vc = np.zeros((N, C2))
    vh = np.zeros((N, C2))

    vw_input_c = _convert_to_chainer_order(vw_input)
    vw_hidden_c = _convert_to_chainer_order(vw_hidden)
    vb_c = _convert_to_chainer_order(vb[None, :])

    for i in range(T):
        vc, vh = lstm(vc, linear(vx[:, i, :], vw_input_c.T) + linear(vh, vw_hidden_c.T) + vb_c)

    vh = vh.data

    x = Variable(vx.shape, order=OrderNTC)
    w_input = ConstantVariable(vw_input, order=OrderCN)
    w_hidden = ConstantVariable(vw_hidden, order=OrderCN)
    b = ConstantVariable(vb, order=OrderC)
    y, = LSTM(None)(x, w_input, w_hidden, b)

    generate_kernel_test_case(
        description=f"LSTM t=1",
        backend=["webassembly", "webgpu"],
        graph=Graph([x], [y]),
        inputs={x: vx},
        expected={y: vh}
    )


def test_t_is_10():
    N = 1
    T = 10
    C1 = 128
    C2 = 64
    vx = np.random.normal(size=(N, T, C1))
    vw_input = np.random.normal(size=(C1, C2 * 4))
    vw_hidden = np.random.normal(size=(C2, C2 * 4))
    vb = np.random.normal(size=(C2 * 4,))
    vc = np.zeros((N, C2))
    vh = np.zeros((N, C2))

    vw_input_c = _convert_to_chainer_order(vw_input)
    vw_hidden_c = _convert_to_chainer_order(vw_hidden)
    vb_c = _convert_to_chainer_order(vb[None, :])

    for i in range(T):
        vc, vh = lstm(vc, linear(vx[:, i, :], vw_input_c.T) + linear(vh, vw_hidden_c.T) + vb_c)

    vh = vh.data

    x = Variable(vx.shape, order=OrderNTC)
    w_input = ConstantVariable(vw_input, order=OrderCN)
    w_hidden = ConstantVariable(vw_hidden, order=OrderCN)
    b = ConstantVariable(vb, order=OrderC)
    y, = LSTM(None)(x, w_input, w_hidden, b)

    generate_kernel_test_case(
        description=f"LSTM t=10",
        backend=["webassembly", "webgpu"],
        graph=Graph([x], [y]),
        inputs={x: vx},
        expected={y: vh}
    )
