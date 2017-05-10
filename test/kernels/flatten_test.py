import numpy as np

from graph_transpiler.graph.axis import Axis
from graph_transpiler.graph.graph import Graph
from graph_transpiler.graph.operators.flatten import Flatten
from graph_transpiler.graph.variable import Variable
from graph_transpiler.graph.variables.attributes.order import OrderNHWC
from test.util import generate_kernel_test_case


def test_no_reorder():
    vx = np.random.rand(2, 1, 1, 5)
    vy = vx.copy()

    x = Variable(vx.shape, order=OrderNHWC)
    y, = Flatten(None, in_axes={Axis.H, Axis.W, Axis.C}, out_axes={Axis.C})(x)

    generate_kernel_test_case(
        description=f"Flatten: H=W=1, no-reorder",
        backend=["webgpu", "webassembly", "fallback"],
        graph=Graph([x], [y]),
        inputs={x: vx},
        expected={y: vy}
    )


def test_reorder():
    vx = np.random.rand(2, 3, 4, 5)
    vy = vx.copy()

    x = Variable(vx.shape, order=OrderNHWC)
    y, = Flatten(None, in_axes={Axis.H, Axis.W, Axis.C}, out_axes={Axis.C})(x)

    generate_kernel_test_case(
        description=f"Flatten: H!=1 && W!=1, reorder",
        backend=["webgpu", "webassembly"],
        graph=Graph([x], [y]),
        inputs={x: vx},
        expected={y: vy}
    )
