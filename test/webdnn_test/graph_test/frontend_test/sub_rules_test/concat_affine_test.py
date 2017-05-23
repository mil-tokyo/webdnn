import itertools

import numpy as np
from nose import with_setup

from test.util import FlagManager
from webdnn.frontend.sub_rules.concat_affine import ConcatAffine
from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.operators.axiswise_bias import AxiswiseBias
from webdnn.graph.operators.axiswise_scale import AxiswiseScale
from webdnn.graph.operators.convolution2d import Convolution2D
from webdnn.graph.order import OrderNHWC, OrderHWNC, OrderNCHW, OrderCNHW, OrderCHWN, \
    OrderHWCN, OrderC
from webdnn.graph.traverse import listup_operators
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable
from webdnn.util import flags

orders4 = [OrderNHWC, OrderHWNC, OrderHWCN, OrderNCHW, OrderCNHW, OrderCHWN]


class ConcatAffineFlagManager(FlagManager):
    def get(self) -> bool:
        return flags.optimize.CONCAT_AFFINE

    def set(self, value: bool):
        flags.optimize.CONCAT_AFFINE = value


flag_manager = ConcatAffineFlagManager()


def arange_shaped(shape):
    return np.arange(np.prod(shape)).reshape(shape).astype(np.float32)


@with_setup(flag_manager.setup, flag_manager.teardown)
def test_conv_scale():
    for order_x, order_w in itertools.product(orders4, orders4):
        conv = Convolution2D(None, ksize=3, stride=1, padding=1)
        scale = AxiswiseScale(None, axis=Axis.C)

        x = Variable([8, 7, 6, 5], OrderNHWC)
        x.change_order(order_x)

        w_shape = [4, 3, 3, 5]
        w = ConstantVariable(arange_shaped(w_shape), OrderNHWC)
        w.change_order(order_w)
        w_data = w.data.copy()

        h, = conv(x, w)

        s_shape = [h.shape_dict[Axis.C]]
        s = ConstantVariable(arange_shaped(s_shape), OrderC)
        s_data = s.data.copy()

        y, = scale(h, s)

        graph = Graph([x], [y])

        graph, _ = ConcatAffine().optimize(graph)

        # noinspection PyTypeChecker
        expander = (None,) * order_w.axes_dict[Axis.N] + (Ellipsis,) + (None,) * (3 - order_w.axes_dict[Axis.N])
        w_data_expected = w_data * s_data[expander]

        ops = listup_operators(graph)
        assert len(ops) == 1 and isinstance(ops[0], Convolution2D)
        assert conv.outputs["y"] == y
        assert np.all(np.equal(w.data, w_data_expected))


@with_setup(flag_manager.setup, flag_manager.teardown)
def test_conv_bias():
    for order_x, order_w in itertools.product(orders4, orders4):
        conv = Convolution2D(None, ksize=3, stride=1, padding=1)
        bias = AxiswiseBias(None, axis=Axis.C)

        x = Variable([8, 7, 6, 5], OrderNHWC)
        x.change_order(order_x)

        w_shape = [4, 3, 3, 5]
        w = ConstantVariable(arange_shaped(w_shape), OrderNHWC)
        w.change_order(order_w)
        w_data = w.data.copy()

        h, = conv(x, w)

        b_shape = [h.shape_dict[Axis.C]]
        b = ConstantVariable(arange_shaped(b_shape), OrderC)
        b_data = b.data.copy()

        y, = bias(h, b)

        graph = Graph([x], [y])

        graph, _ = ConcatAffine().optimize(graph)

        w_data_expected = w_data
        b_data_expected = b_data

        ops = listup_operators(graph)
        assert len(ops) == 2 and isinstance(ops[0], Convolution2D) and isinstance(ops[1], AxiswiseBias)
        assert np.all(np.equal(ops[0].inputs["w"].data, w_data_expected))
        assert np.all(np.equal(ops[1].inputs["b"].data, b_data_expected))


@with_setup(flag_manager.setup, flag_manager.teardown)
def test_conv_scale_scale():
    for order_x, order_w in itertools.product(orders4, orders4):
        conv = Convolution2D(None, ksize=3, stride=1, padding=1)
        scale1 = AxiswiseScale(None, axis=Axis.C)
        scale2 = AxiswiseScale(None, axis=Axis.C)

        x = Variable([8, 7, 6, 5], OrderNHWC)
        x.change_order(order_x)

        w_shape = [4, 3, 3, 5]
        w = ConstantVariable(arange_shaped(w_shape), OrderNHWC)
        w.change_order(order_w)
        w_data = w.data.copy()
        h, = conv(x, w)

        s1_shape = [h.shape_dict[Axis.C]]
        s1 = ConstantVariable(arange_shaped(s1_shape), OrderC)
        s1_data = s1.data.copy()
        h, = scale1(h, s1)

        s2_shape = [h.shape_dict[Axis.C]]
        s2 = ConstantVariable(arange_shaped(s2_shape), OrderC)
        s2_data = s2.data.copy()
        y, = scale2(h, s2)

        graph = Graph([x], [y])

        graph, _ = ConcatAffine().optimize(graph)

        # noinspection PyTypeChecker
        expander = (None,) * order_w.axes_dict[Axis.N] + (Ellipsis,) + (None,) * (3 - order_w.axes_dict[Axis.N])
        w_data_expected = w_data * s1_data[expander] * s2_data[expander]

        ops = listup_operators(graph)
        assert len(ops) == 1 and isinstance(ops[0], Convolution2D)
        assert np.all(np.equal(w.data, w_data_expected))


@with_setup(flag_manager.setup, flag_manager.teardown)
def test_conv_bias_bias():
    for order_x, order_w in itertools.product(orders4, orders4):
        conv = Convolution2D(None, ksize=3, stride=1, padding=1)
        bias1 = AxiswiseBias(None, axis=Axis.C)
        bias2 = AxiswiseBias(None, axis=Axis.C)

        x = Variable([8, 7, 6, 5], OrderNHWC)
        x.change_order(order_x)

        w_shape = [4, 3, 3, 5]
        w = ConstantVariable(arange_shaped(w_shape).copy(), OrderNHWC)
        w.change_order(order_w)
        w_data = w.data.copy()
        h, = conv(x, w)

        b1_shape = [h.shape_dict[Axis.C]]
        b1 = ConstantVariable(arange_shaped(b1_shape), OrderC)
        b1_data = b1.data.copy()
        h, = bias1(h, b1)

        b2_shape = [h.shape_dict[Axis.C]]
        b2 = ConstantVariable(arange_shaped(b2_shape), OrderC)
        b2_data = b2.data.copy()
        y, = bias2(h, b2)

        graph = Graph([x], [y])

        graph, _ = ConcatAffine().optimize(graph)

        w_data_expected = w_data
        b_data_expected = b1_data + b2_data

        ops = listup_operators(graph)
        assert len(ops) == 2 and isinstance(ops[0], Convolution2D) and isinstance(ops[1], AxiswiseBias)
        assert np.all(np.equal(ops[0].inputs["w"].data, w_data_expected))
        assert np.all(np.equal(ops[1].inputs["b"].data, b_data_expected))


@with_setup(flag_manager.setup, flag_manager.teardown)
def test_conv_scale_bias():
    for order_x, order_w in itertools.product(orders4, orders4):
        conv = Convolution2D(None, ksize=3, stride=1, padding=1)
        scale = AxiswiseScale(None, axis=Axis.C)
        bias = AxiswiseBias(None, axis=Axis.C)

        x = Variable([8, 7, 6, 5], OrderNHWC)
        x.change_order(order_x)

        w_shape = [4, 3, 3, 5]
        w = ConstantVariable(arange_shaped(w_shape), OrderNHWC)
        w.change_order(order_w)
        w_data = w.data.copy()
        h, = conv(x, w)

        s_shape = [h.shape_dict[Axis.C]]
        s = ConstantVariable(arange_shaped(s_shape), OrderC)
        s_data = s.data.copy()
        h, = scale(h, s)

        b_shape = [h.shape_dict[Axis.C]]
        b = ConstantVariable(arange_shaped(b_shape), OrderC)
        b_data = b.data.copy()
        y, = bias(h, b)

        graph = Graph([x], [y])

        graph, _ = ConcatAffine().optimize(graph)

        # noinspection PyTypeChecker
        expander = (None,) * order_w.axes_dict[Axis.N] + (Ellipsis,) + (None,) * (3 - order_w.axes_dict[Axis.N])
        w_data_expected = w_data * s_data[expander]
        b_data_expected = b_data

        ops = listup_operators(graph)
        assert len(ops) == 2 and isinstance(ops[0], Convolution2D) and isinstance(ops[1], AxiswiseBias)
        assert np.all(np.equal(ops[0].inputs["w"].data, w_data_expected))
        assert np.all(np.equal(ops[1].inputs["b"].data, b_data_expected))


@with_setup(flag_manager.setup, flag_manager.teardown)
def test_conv_bias_scale():
    for order_x, order_w in itertools.product(orders4, orders4):
        conv = Convolution2D(None, ksize=3, stride=1, padding=1)
        bias = AxiswiseBias(None, axis=Axis.C)
        scale = AxiswiseScale(None, axis=Axis.C)

        x = Variable([8, 7, 6, 5], OrderNHWC)
        x.change_order(order_x)

        w_shape = [4, 3, 3, 5]
        w = ConstantVariable(arange_shaped(w_shape), OrderNHWC)
        w.change_order(order_w)
        w_data = w.data.copy()
        h, = conv(x, w)

        b_shape = [h.shape_dict[Axis.C]]
        b = ConstantVariable(arange_shaped(b_shape), OrderC)
        b_data = b.data.copy()
        h, = bias(h, b)

        s_shape = [h.shape_dict[Axis.C]]
        s = ConstantVariable(arange_shaped(s_shape), OrderC)
        s_data = s.data.copy()
        y, = scale(h, s)

        graph = Graph([x], [y])

        graph, _ = ConcatAffine().optimize(graph)

        # noinspection PyTypeChecker
        expander = (None,) * order_w.axes_dict[Axis.N] + (Ellipsis,) + (None,) * (3 - order_w.axes_dict[Axis.N])
        w_data_expected = w_data * s_data[expander]
        b_data_expected = b_data * s_data

        ops = listup_operators(graph)
        assert len(ops) == 2 and isinstance(ops[0], Convolution2D) and isinstance(ops[1], AxiswiseBias)
        assert np.all(np.equal(ops[0].inputs["w"].data, w_data_expected))
        assert np.all(np.equal(ops[1].inputs["b"].data, b_data_expected))
