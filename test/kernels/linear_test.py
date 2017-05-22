import numpy as np

from test.util import generate_kernel_test_case
from webdnn.graph.graph import Graph
from webdnn.graph.operators.linear import Linear
from webdnn.graph.order import OrderNC, OrderCN, OrderHWCN, OrderNHWC
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable


def test_NC_CN():
    vx = np.random.rand(3, 4)
    vw = np.random.rand(4, 5)
    vy = np.dot(vx, vw)

    x = Variable(vx.shape, order=OrderNC)
    w = ConstantVariable(vw, order=OrderCN)
    y1, = Linear(None)(x, w)
    y2, = Linear(None)(x, w)
    y3, = Linear(None)(x, w)

    generate_kernel_test_case(
        description=f"Linear: NC*CN",
        backend=["fallback"],
        graph=Graph([x], [y1]),
        inputs={x: vx},
        expected={y1: vy},
        raise_skip=False
    )

    generate_kernel_test_case(
        description=f"Linear: NC*CN",
        backend=["webgpu"],
        graph=Graph([x], [y2]),
        inputs={x: vx},
        expected={y2: vy},
        raise_skip=False
    )

    generate_kernel_test_case(
        description=f"Linear: NC*CN",
        backend="webassembly",
        graph=Graph([x], [y3]),
        inputs={x: vx},
        expected={y3: vy}
    )


def test_NHWC_HWCN():
    vx = np.random.rand(2, 3, 4, 5)
    vw = np.random.rand(3, 4, 5, 2)
    vy = np.tensordot(vx, vw, ((1, 2, 3), (0, 1, 2)))

    x = Variable(vx.shape, order=OrderNHWC)
    w = ConstantVariable(vw, order=OrderHWCN)
    y1, = Linear(None)(x, w)
    y2, = Linear(None)(x, w)
    y3, = Linear(None)(x, w)

    generate_kernel_test_case(
        description=f"Linear: NHWC*HWCN",
        backend=["fallback"],
        graph=Graph([x], [y1]),
        inputs={x: vx},
        expected={y1: vy},
        raise_skip=False
    )

    generate_kernel_test_case(
        description=f"Linear: NHWC*HWCN",
        backend=["webgpu"],
        graph=Graph([x], [y2]),
        inputs={x: vx},
        expected={y2: vy},
        raise_skip=False
    )

    generate_kernel_test_case(
        description=f"Linear: NHWC*HWCN",
        backend="webassembly",
        graph=Graph([x], [y3]),
        inputs={x: vx},
        expected={y3: vy}
    )
