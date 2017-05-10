import numpy as np

from graph_transpiler.graph.axis import Axis
from graph_transpiler.graph.graph import Graph
from graph_transpiler.graph.operators.axiswise_bias import AxiswiseBias
from graph_transpiler.graph.variable import Variable
from graph_transpiler.graph.variables.attributes.order import OrderC, OrderNC, OrderNHWC, OrderHWNC
from graph_transpiler.graph.variables.constant_variable import ConstantVariable
from test.util import generate_kernel_test_case


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
