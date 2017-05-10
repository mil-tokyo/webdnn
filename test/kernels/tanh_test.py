import numpy as np

from graph_transpiler.graph.graph import Graph
from graph_transpiler.graph.operators.tanh import Tanh
from graph_transpiler.graph.variable import Variable
from graph_transpiler.graph.variables.attributes.order import OrderNHWC
from test.util import generate_kernel_test_case


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
