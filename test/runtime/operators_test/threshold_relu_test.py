import numpy as np

from test.util import generate_kernel_test_case
from webdnn.graph.graph import Graph
from webdnn.graph.operators.threshold_relu import ThresholdRelu
from webdnn.graph.order import OrderNHWC
from webdnn.graph.variable import Variable


def test_general():
    vx = np.random.rand(2, 3, 4, 5) * 5
    vy = vx * (vx > 2)

    x = Variable(vx.shape, order=OrderNHWC)
    y, = ThresholdRelu(None, threshold=2)(x)

    generate_kernel_test_case(
        description=f"ThresholdRelu",
        backend=["webgpu", "webassembly", "fallback"],
        graph=Graph([x], [y]),
        inputs={x: vx},
        expected={y: vy}
    )
