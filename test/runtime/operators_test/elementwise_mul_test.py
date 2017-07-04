import numpy as np

from test.util import generate_kernel_test_case
from webdnn.graph.graph import Graph
from webdnn.graph.operators.elementwise_mul import ElementwiseMul
from webdnn.graph.operators.elementwise_sum import ElementwiseSum
from webdnn.graph.order import OrderNHWC
from webdnn.graph.variable import Variable


def test_general():
    vx1 = np.random.rand(2, 3, 4, 5)
    vx2 = np.random.rand(2, 3, 4, 5)
    vy = vx1 * vx2

    x1 = Variable(vx1.shape, order=OrderNHWC)
    x2 = Variable(vx2.shape, order=OrderNHWC)
    y, = ElementwiseMul(None)(x1, x2)

    generate_kernel_test_case(
        description=f"ElementwiseMul",
        backend=["webgpu", "webassembly", "fallback"],
        graph=Graph([x1, x2], [y]),
        inputs={x1: vx1, x2: vx2},
        expected={y: vy}
    )
