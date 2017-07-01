import numpy as np

from test.util import generate_kernel_test_case
from webdnn.graph.graph import Graph
from webdnn.graph.operators.scalar_affine import ScalarAffine
from webdnn.graph.order import OrderNC
from webdnn.graph.variable import Variable


def test_scalar_affine():
    vx = np.random.rand(2, 3)
    vy = vx * 4 + 5

    x = Variable(vx.shape, order=OrderNC)
    y, = ScalarAffine(None, scale=4, bias=5)(x)

    generate_kernel_test_case(
        description=f"ScalarAffine",
        backend="webgpu",
        graph=Graph([x], [y]),
        inputs={x: vx},
        expected={y: vy}
    )
