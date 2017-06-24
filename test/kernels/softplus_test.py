import numpy as np

from test.util import generate_kernel_test_case
from webdnn.graph.graph import Graph
from webdnn.graph.operators.softplus import Softplus
from webdnn.graph.order import OrderNHWC
from webdnn.graph.variable import Variable


def test_general():
    beta = 2.0
    vx = np.random.rand(2, 3, 4, 5) - 0.5
    vy = np.log(np.exp(vx * beta) + 1.0) / beta

    x = Variable(vx.shape, order=OrderNHWC)
    y, = Softplus(None, beta=beta)(x)

    generate_kernel_test_case(
        description=f"Softplus",
        backend=["webgpu", "webassembly", "fallback"],
        graph=Graph([x], [y]),
        inputs={x: vx},
        expected={y: vy}
    )
