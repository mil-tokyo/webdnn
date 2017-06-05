import numpy as np

from test.util import generate_kernel_test_case
from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.operators.axiswise_bias import AxiswiseBias
from webdnn.graph.order import OrderC, OrderNHWC, OrderNCHW, OrderCNHW
from webdnn.graph.variable import Variable


def test_minor_axis():
    vx = np.random.rand(10, 6, 4, 8)
    vb = np.random.rand(8)
    vy = vx + vb[None, None, None, :]

    x = Variable(vx.shape, order=OrderNHWC)
    b = Variable(vb.shape, order=OrderC)
    y, = AxiswiseBias(None, axis=Axis.C)(x, b)

    generate_kernel_test_case(
        description=f"AxiswiseBias for minor axis",
        backend=["webgpu", "webassembly", "fallback"],
        graph=Graph([x, b], [y]),
        inputs={x: vx, b: vb},
        expected={y: vy}
    )


def test_middle_axis():
    vx = np.random.rand(10, 6, 4, 8)
    vb = np.random.rand(6)
    vy = vx + vb[None, :, None, None]

    x = Variable(vx.shape, order=OrderNCHW)
    b = Variable(vb.shape, order=OrderC)
    y, = AxiswiseBias(None, axis=Axis.C)(x, b)

    generate_kernel_test_case(
        description=f"AxiswiseBias for middle axis",
        backend=["webgpu", "fallback"],
        graph=Graph([x, b], [y]),
        inputs={x: vx, b: vb},
        expected={y: vy}
    )


def test_major_axis():
    vx = np.random.rand(10, 6, 4, 8)
    vb = np.random.rand(10)
    vy = vx + vb[:, None, None, None]

    x = Variable(vx.shape, order=OrderCNHW)
    b = Variable(vb.shape, order=OrderC)
    y, = AxiswiseBias(None, axis=Axis.C)(x, b)

    generate_kernel_test_case(
        description=f"AxiswiseBias for major axis",
        backend=["webgpu", "fallback"],
        graph=Graph([x, b], [y]),
        inputs={x: vx, b: vb},
        expected={y: vy}
    )


def test_mix_order():
    vx = np.random.rand(10, 6, 4, 8)
    vb = np.random.rand(10)
    vy = vx + vb[:, None, None, None]

    x = Variable(vx.shape, order=OrderCNHW)
    b = Variable(vb.shape, order=OrderC)
    y, = AxiswiseBias(None, axis=Axis.C)(x, b)

    x.change_order(OrderNHWC)
    vx = np.rollaxis(vx, 0, 4)

    generate_kernel_test_case(
        description=f"AxiswiseBias for mix order",
        backend=["webgpu"],
        graph=Graph([x, b], [y]),
        inputs={x: vx, b: vb},
        expected={y: vy}
    )
