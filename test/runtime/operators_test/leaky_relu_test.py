import numpy as np

from test.util import generate_kernel_test_case
from webdnn.graph.graph import Graph
from webdnn.graph.operators.leaky_relu import LeakyRelu
from webdnn.graph.order import OrderNHWC
from webdnn.graph.variable import Variable


def test_general():
    slope = 0.5
    vx = np.random.rand(2, 3, 4, 5) - 0.5
    vy = np.maximum(vx, vx * slope)

    x = Variable(vx.shape, order=OrderNHWC)
    y, = LeakyRelu(None, slope=slope)(x)

    generate_kernel_test_case(
        description=f"LeakyRelu",
        backend=["webgpu", "webassembly", "fallback"],
        graph=Graph([x], [y]),
        inputs={x: vx},
        expected={y: vy}
    )
