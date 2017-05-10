import numpy as np

from graph_builder.graph.axis import Axis
from graph_builder.graph.graph import Graph
from graph_builder.graph.operators.axiswise_scale import AxiswiseScale
from graph_builder.graph.variable import Variable
from graph_builder.graph.variables.attributes.order import OrderC, OrderNC, OrderNHWC, OrderHWNC
from graph_builder.graph.variables.constant_variable import ConstantVariable
from test.util import generate_kernel_test_case


def test_NC():
    vx = np.random.rand(10, 8)
    vs = np.random.rand(8)
    vy = vx * vs[None, :]

    x = Variable(vx.shape, order=OrderNC)
    s = ConstantVariable(vs, order=OrderC)
    y, = AxiswiseScale(None, axis=Axis.C)(x, s)

    generate_kernel_test_case(
        description=f"AxiswiseScale for input OrderNC",
        backend=["webgpu", "webassembly", "fallback"],
        graph=Graph([x], [y]),
        inputs={x: vx},
        expected={y: vy}
    )


def test_HWNC():
    vx = np.random.rand(6, 4, 10, 8)
    vs = np.random.rand(8)
    vy = vx * vs[None, None, None, :]

    x = Variable(vx.shape, order=OrderHWNC)
    s = ConstantVariable(vs, order=OrderC)
    y, = AxiswiseScale(None, axis=Axis.C)(x, s)

    generate_kernel_test_case(
        description=f"AxiswiseScale for input OrderHWNC",
        backend=["webgpu", "webassembly", "fallback"],
        graph=Graph([x], [y]),
        inputs={x: vx},
        expected={y: vy}
    )


def test_NHWC():
    vx = np.random.rand(10, 6, 4, 8)
    vs = np.random.rand(8)
    vy = vx * vs[None, None, None, :]

    x = Variable(vx.shape, order=OrderNHWC)
    s = ConstantVariable(vs, order=OrderC)
    y, = AxiswiseScale(None, axis=Axis.C)(x, s)

    generate_kernel_test_case(
        description=f"AxiswiseScale for input OrderNHWC",
        backend=["webgpu", "webassembly", "fallback"],
        graph=Graph([x], [y]),
        inputs={x: vx},
        expected={y: vy}
    )
