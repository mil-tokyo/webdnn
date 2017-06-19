import numpy as np

from test.util import generate_kernel_test_case
from webdnn.graph.graph import Graph
from webdnn.graph.operators.embedding import Embedding
from webdnn.graph.order import OrderNT, OrderCN
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable


def test_general():
    vx = np.array([[2, 4, 3]])
    vw = np.arange(15).reshape(5, 3)
    vy = vw[vx]

    x = Variable(vx.shape, order=OrderNT)
    w = ConstantVariable(vw, order=OrderCN)
    y, = Embedding(None)(x, w)

    generate_kernel_test_case(
        description=f"Embedding",
        backend=["webgpu"],
        graph=Graph([x], [y]),
        inputs={x: vx},
        expected={y: vy}
    )
