import numpy as np

from test.util import generate_kernel_test_case
from webdnn.graph.graph import Graph
from webdnn.graph.operators.hard_sigmoid import HardSigmoid
from webdnn.graph.order import OrderNHWC
from webdnn.graph.variable import Variable


def test_general():
    vx = np.random.rand(2, 3, 4, 5) - 0.5
    vy = np.clip(vx * 0.2 + 0.5, 0.0, 1.0)

    x = Variable(vx.shape, order=OrderNHWC)
    y, = HardSigmoid(None)(x)

    generate_kernel_test_case(
        description=f"HardSigmoid",
        backend=["webgpu", "webassembly", "fallback"],
        graph=Graph([x], [y]),
        inputs={x: vx},
        expected={y: vy}
    )
