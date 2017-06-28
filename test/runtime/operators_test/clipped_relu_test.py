import numpy as np

from test.util import generate_kernel_test_case
from webdnn.graph.graph import Graph
from webdnn.graph.operators.clipped_relu import ClippedRelu
from webdnn.graph.order import OrderNHWC
from webdnn.graph.variable import Variable


def test_general():
    cap = 0.25
    vx = np.random.rand(2, 3, 4, 5) - 0.5
    vy = np.clip(vx, 0.0, cap)

    x = Variable(vx.shape, order=OrderNHWC)
    y, = ClippedRelu(None, cap=cap)(x)

    generate_kernel_test_case(
        description=f"ClippedRelu",
        backend=["webgpu", "webassembly", "fallback"],
        graph=Graph([x], [y]),
        inputs={x: vx},
        expected={y: vy}
    )
