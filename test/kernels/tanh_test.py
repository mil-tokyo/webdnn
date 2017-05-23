import numpy as np

from test.util import generate_kernel_test_case
from webdnn.graph.graph import Graph
from webdnn.graph.operators.tanh import Tanh
from webdnn.graph.order import OrderNHWC
from webdnn.graph.variable import Variable


def test_general():
    vx = np.random.rand(2, 3, 4, 5) - 0.5
    vy = np.tanh(vx)

    x = Variable(vx.shape, order=OrderNHWC)
    y, = Tanh(None)(x)

    generate_kernel_test_case(
        description=f"Tanh",
        backend=["webgpu", "webassembly"],
        graph=Graph([x], [y]),
        inputs={x: vx},
        expected={y: vy}
    )
