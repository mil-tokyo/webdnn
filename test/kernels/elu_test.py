import numpy as np

from graph_builder.graph.graph import Graph
from graph_builder.graph.operators.elu import Elu
from graph_builder.graph.variable import Variable
from graph_builder.graph.variables.attributes.order import OrderNHWC
from test.util import generate_kernel_test_case


def test_general():
    vx = np.random.rand(2, 3, 4, 5) - 0.5
    vy = vx.copy()
    vy[vx < 0] = np.exp(vy[vx < 0]) - 1

    x = Variable(vx.shape, order=OrderNHWC)
    y, = Elu(None)(x)

    generate_kernel_test_case(
        description=f"Elu",
        backend=["webgpu", "webassembly"],
        graph=Graph([x], [y]),
        inputs={x: vx},
        expected={y: vy}
    )
