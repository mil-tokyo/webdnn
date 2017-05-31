import numpy as np

from test.util import generate_kernel_test_case
from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.operators.concat import Concat
from webdnn.graph.order import OrderNHWC
from webdnn.graph.variable import Variable


def test_major_axis():
    vx1 = np.random.rand(2, 3, 4, 5)
    vx2 = np.random.rand(2, 3, 4, 5)
    vx3 = np.random.rand(2, 3, 4, 5)
    vx4 = np.random.rand(2, 3, 4, 5)
    vy = np.concatenate((vx1, vx2, vx3, vx4), 0)

    x1 = Variable(vx1.shape, order=OrderNHWC)
    x2 = Variable(vx2.shape, order=OrderNHWC)
    x3 = Variable(vx3.shape, order=OrderNHWC)
    x4 = Variable(vx4.shape, order=OrderNHWC)
    y, = Concat(None, axis=Axis.N)(x1, x2, x3, x4)

    generate_kernel_test_case(
        description=f"concat_in_major_axis",
        backend=["webgpu"],
        graph=Graph([x1, x2, x3, x4], [y]),
        inputs={
            x1: vx1,
            x2: vx2,
            x3: vx3,
            x4: vx4
        },
        expected={y: vy}
    )
