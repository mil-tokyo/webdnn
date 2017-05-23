import numpy as np

from test.util import generate_kernel_test_case
from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.operators.flatten import Flatten
from webdnn.graph.order import OrderNHWC
from webdnn.graph.variable import Variable


def test_no_reorder():
    vx = np.random.rand(2, 1, 1, 5)
    vy = vx.copy()

    x = Variable(vx.shape, order=OrderNHWC)
    y, = Flatten(None, in_axes=[Axis.H, Axis.W, Axis.C], out_axis=Axis.C)(x)

    generate_kernel_test_case(
        description=f"Flatten: H=W=1, no-reorder",
        backend=["webgpu", "webassembly", "fallback"],
        graph=Graph([x], [y]),
        inputs={x: vx},
        expected={y: vy}
    )
