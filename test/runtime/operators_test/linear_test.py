import numpy as np

from test.util import generate_kernel_test_case
from webdnn.graph.graph import Graph
from webdnn.graph.operators.linear import Linear
from webdnn.graph.order import OrderNC, OrderCN, OrderHWCN, OrderNHWC
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable


def test_NC_CN():
    vx = np.random.rand(3, 4).astype(np.float32)
    vw = np.random.rand(4, 5).astype(np.float32)
    vy = np.dot(vx, vw)

    x = Variable(vx.shape, order=OrderNC)
    w = ConstantVariable(vw, order=OrderCN)
    y, = Linear(None)(x, w)

    generate_kernel_test_case(
        description=f"Linear: NC*CN",
        backend=["fallback", "webgl", "webassembly", "webgpu"],
        graph=Graph([x], [y]),
        inputs={x: vx},
        expected={y: vy},
        raise_skip=False
    )


def test_NHWC_HWCN():
    vx = np.random.rand(2, 3, 4, 5).astype(np.float32)
    vw = np.random.rand(3, 4, 5, 2).astype(np.float32)
    vy = np.tensordot(vx, vw, ((1, 2, 3), (0, 1, 2)))

    x = Variable(vx.shape, order=OrderNHWC)
    w = ConstantVariable(vw, order=OrderHWCN)
    y, = Linear(None)(x, w)

    generate_kernel_test_case(
        description=f"Linear: NHWC*HWCN",
        backend=["fallback", "webgl", "webassembly", "webgpu"],
        graph=Graph([x], [y]),
        inputs={x: vx},
        expected={y: vy},
        raise_skip=False
    )
