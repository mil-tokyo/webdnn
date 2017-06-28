import numpy as np

from test.util import generate_kernel_test_case
from webdnn.graph.graph import Graph
from webdnn.graph.operators.elu import Elu
from webdnn.graph.order import OrderNHWC
from webdnn.graph.variable import Variable


def test_general():
    vx = np.random.rand(2, 3, 4, 5) - 0.5
    vy = vx.copy()
    vy[vx < 0] = np.exp(vy[vx < 0]) - 1

    x = Variable(vx.shape, order=OrderNHWC)
    y, = Elu(None)(x)

    generate_kernel_test_case(
        description=f"Elu",
        backend=["webgpu", "webassembly", "fallback"],
        graph=Graph([x], [y]),
        inputs={x: vx},
        expected={y: vy}
    )
