import numpy as np

from test.util import generate_kernel_test_case
from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.operators.split_axis import SplitAxis
from webdnn.graph.order import OrderNHWC, OrderCNHW, OrderCHWN, OrderNCHW
from webdnn.graph.variable import Variable


def test_major_axis():
    vx1 = np.random.rand(2, 3, 4, 5)
    vx2 = np.random.rand(2, 3, 4, 5)
    vx3 = np.random.rand(2, 3, 4, 5)
    vx4 = np.random.rand(2, 3, 4, 5)
    vy = np.concatenate((vx1, vx2, vx3, vx4), 0)

    y = Variable(vy.shape, order=OrderNHWC)
    x1, x2, x3, x4, = SplitAxis(None, axis=Axis.N, sections=[2, 4, 6])(y)

    generate_kernel_test_case(
        description=f"SplitAxis in major axis",
        backend=["webgpu", "webassembly", "fallback"],
        graph=Graph([y], [x1, x2, x3, x4]),
        inputs={y: vy},
        expected={
            x1: vx1,
            x2: vx2,
            x3: vx3,
            x4: vx4
        }
    )


def test_minor_axis():
    vx1 = np.random.rand(2, 3, 4, 5)
    vx2 = np.random.rand(2, 3, 4, 5)
    vx3 = np.random.rand(2, 3, 4, 5)
    vx4 = np.random.rand(2, 3, 4, 5)
    vy = np.concatenate((vx1, vx2, vx3, vx4), 3)

    y = Variable(vy.shape, order=OrderNHWC)
    x1, x2, x3, x4, = SplitAxis(None, axis=Axis.C, sections=[5, 10, 15])(y)

    generate_kernel_test_case(
        description=f"SplitAxis in minor axis",
        backend=["webgpu", "webassembly", "fallback"],
        graph=Graph([y], [x1, x2, x3, x4]),
        inputs={y: vy},
        expected={
            x1: vx1,
            x2: vx2,
            x3: vx3,
            x4: vx4
        }
    )


def test_middle_axis():
    vx1 = np.random.rand(2, 3, 4, 5)
    vx2 = np.random.rand(2, 3, 4, 5)
    vx3 = np.random.rand(2, 3, 4, 5)
    vx4 = np.random.rand(2, 3, 4, 5)
    vy = np.concatenate((vx1, vx2, vx3, vx4), 1)

    y = Variable(vy.shape, order=OrderNHWC)
    x1, x2, x3, x4, = SplitAxis(None, axis=Axis.H, sections=[3, 6, 9])(y)

    generate_kernel_test_case(
        description=f"SplitAxis in middle axis",
        backend=["webgpu", "webassembly", "fallback"],
        graph=Graph([y], [x1, x2, x3, x4]),
        inputs={y: vy},
        expected={
            x1: vx1,
            x2: vx2,
            x3: vx3,
            x4: vx4
        }
    )


def test_mix_order():
    vx1 = np.random.rand(2, 3, 4, 5)
    vx2 = np.random.rand(2, 3, 4, 5)
    vx3 = np.random.rand(2, 3, 4, 5)
    vx4 = np.random.rand(2, 3, 4, 5)
    vy = np.concatenate((vx1, vx2, vx3, vx4), 1)

    y = Variable(vy.shape, order=OrderNHWC)
    x1, x2, x3, x4, = SplitAxis(None, axis=Axis.H, sections=[3, 6, 9])(y)

    x2.change_order(OrderCNHW)
    vx2 = np.rollaxis(vx2, 3, 0)

    x3.change_order(OrderCHWN)
    vx3 = np.rollaxis(np.rollaxis(vx3, 3, 0), 1, 4)

    x4.change_order(OrderNCHW)
    vx4 = np.rollaxis(vx4, 3, 1)

    generate_kernel_test_case(
        description=f"SplitAxis with mix order",
        backend=["webgpu", "webassembly", "fallback"],
        graph=Graph([y], [x1, x2, x3, x4]),
        inputs={y: vy},
        expected={
            x1: vx1,
            x2: vx2,
            x3: vx3,
            x4: vx4
        }
    )
