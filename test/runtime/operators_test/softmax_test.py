import numpy as np

from test.util import generate_kernel_test_case
from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.operators.softmax import Softmax
from webdnn.graph.order import OrderNC
from webdnn.graph.variable import Variable


def test_general():
    vx = np.random.rand(2, 5) - 0.5
    vy = np.exp(vx) / np.sum(np.exp(vx), axis=1, keepdims=True)

    x = Variable(vx.shape, order=OrderNC)
    y, = Softmax(None, axis=Axis.C)(x)

    generate_kernel_test_case(
        description=f"Softmax",
        backend=["webgpu", "webassembly", "fallback"],
        graph=Graph([x], [y]),
        inputs={x: vx},
        expected={y: vy}
    )
