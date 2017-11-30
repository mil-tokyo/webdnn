import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn.graph.axis import AxisKeyDict, Axis
from webdnn.graph.graph import Graph
from webdnn.graph.operators.slice import Slice
from webdnn.graph.order import OrderNHWC, OrderNC, OrderNCHW
from webdnn.graph.variable import Variable


@wrap_template
def template(x_shape=[3, 6], x_order=OrderNC, y_order=OrderNC, indices=AxisKeyDict([Axis.N, Axis.C], [slice(None), slice(None)]),
             description: str = ""):
    # vx = np.random.rand(*x_shape)
    vx = np.arange(np.product(x_shape)).reshape(x_shape)
    x_remain_axes = [a for a in x_order.axes if a in y_order.axes]
    vy = np.transpose(vx[tuple(indices[a] for a in x_order.axes)], [x_remain_axes.index(a) for a in y_order.axes if a in x_remain_axes])
    for i, a in enumerate(y_order.axes):
        if a not in x_order.axes:
            vy = np.expand_dims(vy, i)

    x = Variable(vx.shape, order=x_order)
    y, = Slice(None, indices=indices)(x)

    y.change_order(y_order)

    assert list(vy.shape) == list(y.shape)

    generate_kernel_test_case(
        description=f"Slice {description}",
        graph=Graph([x], [y]),
        backend=["webgpu", "webgl", "webassembly"],
        inputs={x: vx},
        expected={y: vy},
    )


def test():
    template(x_shape=[3, 4, 5, 6], x_order=OrderNHWC, y_order=OrderNHWC, indices=AxisKeyDict(
        [Axis.N, Axis.H, Axis.W, Axis.C],
        [slice(0, 2), slice(1, 3), slice(2, 4), slice(3, 5)]
    ), description="normal")


def test_change_order():
    template(x_shape=[3, 4, 5, 6], x_order=OrderNHWC, y_order=OrderNCHW, indices=AxisKeyDict(
        [Axis.N, Axis.H, Axis.W, Axis.C],
        [slice(0, 2), slice(1, 3), slice(2, 4), slice(3, 5)]
    ), description="change order")


def test_no_slice():
    template(x_shape=[3, 4, 5, 6], x_order=OrderNHWC, y_order=OrderNHWC, indices=AxisKeyDict(
        [Axis.N, Axis.H, Axis.W, Axis.C],
        [slice(None), slice(None), slice(None), slice(None)]
    ), description="no slice")


def test_remove_axis():
    template(x_shape=[3, 4, 5, 6], x_order=OrderNHWC, y_order=OrderNC, indices=AxisKeyDict(
        [Axis.N, Axis.H, Axis.W, Axis.C],
        [slice(0, 2), 2, 4, slice(3, 5)]
    ), description="remove axis")


def test_insert_axis():
    template(x_shape=[3, 6], x_order=OrderNC, y_order=OrderNHWC, indices=AxisKeyDict(
        [Axis.N, Axis.H, Axis.W, Axis.C],
        [slice(0, 2), None, None, slice(3, 5)]
    ), description="insert axis")


def test_large_step():
    template(x_shape=[3, 6], x_order=OrderNC, y_order=OrderNC, indices=AxisKeyDict(
        [Axis.N, Axis.C],
        [slice(0, 2), slice(0, 6, 2)]
    ), description="large step")


def test_reverse_index():
    template(x_shape=[3, 6], x_order=OrderNC, y_order=OrderNC, indices=AxisKeyDict(
        [Axis.N, Axis.C],
        [slice(0, 2), slice(5, 1, -1)]
    ), description="reverse index")
