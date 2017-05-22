import numpy as np

from test.util import generate_kernel_test_case
from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.operators.axiswise_bias import AxiswiseBias
from webdnn.graph.order import OrderC, OrderNC, OrderNHWC, OrderHWNC
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable


def test_NC():
    vx = np.random.rand(10, 8)
    vb = np.random.rand(8)
    vy = vx + vb[None, :]

    x = Variable(vx.shape, order=OrderNC)
    b = ConstantVariable(vb, order=OrderC)
    y, = AxiswiseBias(None, axis=Axis.C)(x, b)

    generate_kernel_test_case(
        description=f"AxiswiseBias for input OrderNC",
        backend=["webgpu", "webassembly", "fallback"],
        graph=Graph([x], [y]),
        inputs={x: vx},
        expected={y: vy}
    )


def test_HWNC():
    vx = np.random.rand(6, 4, 10, 8)
    vb = np.random.rand(8)
    vy = vx + vb[None, None, None, :]

    x = Variable(vx.shape, order=OrderHWNC)
    b = ConstantVariable(vb, order=OrderC)
    y, = AxiswiseBias(None, axis=Axis.C)(x, b)

    generate_kernel_test_case(
        description=f"AxiswiseBias for input OrderHWNC",
        backend=["webgpu", "webassembly", "fallback"],
        graph=Graph([x], [y]),
        inputs={x: vx},
        expected={y: vy}
    )


def test_NHWC():
    vx = np.random.rand(10, 6, 4, 8)
    vb = np.random.rand(8)
    vy = vx + vb[None, None, None, :]

    x = Variable(vx.shape, order=OrderNHWC)
    b = ConstantVariable(vb, order=OrderC)
    y, = AxiswiseBias(None, axis=Axis.C)(x, b)

    generate_kernel_test_case(
        description=f"AxiswiseBias for input OrderNHWC",
        backend=["webgpu", "webassembly", "fallback"],
        graph=Graph([x], [y]),
        inputs={x: vx},
        expected={y: vy}
    )
