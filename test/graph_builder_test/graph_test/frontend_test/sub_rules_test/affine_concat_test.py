import itertools

import numpy as np
from nose import with_setup

from graph_builder.frontend.sub_rules.affine_concat import AffineConcat
from graph_builder.graph.axis import Axis
from graph_builder.graph.graph import Graph
from graph_builder.graph.operators.axiswise_bias import AxiswiseBias
from graph_builder.graph.operators.axiswise_scale import AxiswiseScale
from graph_builder.graph.operators.convolution2d import Convolution2D
from graph_builder.graph.variable import Variable
from graph_builder.graph.variables.attributes.order import OrderNHWC, OrderHWNC, OrderNCHW, OrderCNHW, OrderCHWN, OrderHWCN, OrderC
from graph_builder.graph.variables.constant_variable import ConstantVariable
from graph_builder.optimize_rule.util import listup_operators
from graph_builder.util import flags
from test.util import FlagManager

orders4 = [OrderNHWC, OrderHWNC, OrderHWCN, OrderNCHW, OrderCNHW, OrderCHWN]


class AffineConcatFlagManager(FlagManager):
    def get(self) -> bool:
        return flags.optimize.AFFINE_CONCAT

    def set(self, value: bool):
        flags.optimize.AFFINE_CONCAT = value


flag_manager = AffineConcatFlagManager()


@with_setup(flag_manager.setup, flag_manager.teardown)
def test_conv_scale():
    for order_x, order_w in itertools.product(orders4, orders4):
        conv = Convolution2D('conv', {'ksize': (3, 3), 'stride': (1, 1), 'padding': (1, 1)})
        scale = AxiswiseScale('scale', {'axis': Axis.C})

        x = Variable([8, 7, 6, 5], OrderNHWC)
        x.change_axis_order(order_x)

        w_shape = [4, 3, 3, 5]
        w_size: int = np.prod(w_shape)
        w = ConstantVariable(np.arange(w_size).reshape(w_shape), OrderNHWC)
        w.change_axis_order(order_w)
        w_data = w.data.copy()

        h, = conv(x, w)

        s_shape = [h.shape_dict[Axis.C]]
        s_size: int = np.prod(s_shape)
        s = ConstantVariable(np.arange(s_size).reshape(s_shape), OrderC)
        s_data = s.data.copy()

        y, = scale(h, s)

        graph = Graph([x], [y])

        graph, _ = AffineConcat().optimize(graph)

        expander = (None,) * order_w.axes_dict[Axis.N] + (Ellipsis,) + (None,) * (3 - order_w.axes_dict[Axis.N])
        w_data_expected = w_data * s_data[expander]

        ops = listup_operators(graph)
        assert len(ops) == 1 and isinstance(ops[0], Convolution2D)
        assert conv.outputs["y"] == y
        assert np.all(np.equal(w.data, w_data_expected))


@with_setup(flag_manager.setup, flag_manager.teardown)
def test_conv_bias():
    for order_x, order_w in itertools.product(orders4, orders4):
        conv = Convolution2D('conv', {'ksize': (3, 3), 'stride': (1, 1), 'padding': (1, 1)})
        bias = AxiswiseBias('bias', {'axis': Axis.C})

        x = Variable([8, 7, 6, 5], OrderNHWC)
        x.change_axis_order(order_x)

        w_shape = [4, 3, 3, 5]
        w_size: int = np.prod(w_shape)
        w = ConstantVariable(np.arange(w_size).reshape(w_shape), OrderNHWC)
        w.change_axis_order(order_w)
        w_data = w.data.copy()

        h, = conv(x, w)

        b_shape = [h.shape_dict[Axis.C]]
        b_size: int = np.prod(b_shape)
        b = ConstantVariable(np.arange(b_size).reshape(b_shape), OrderC)
        b_data = b.data.copy()

        y, = bias(h, b)

        graph = Graph([x], [y])

        graph, _ = AffineConcat().optimize(graph)

        w_data_expected = w_data
        b_data_expected = b_data

        ops = listup_operators(graph)
        assert len(ops) == 2 and isinstance(ops[0], Convolution2D) and isinstance(ops[1], AxiswiseBias)
        assert np.all(np.equal(ops[0].inputs["w"].data, w_data_expected))
        assert np.all(np.equal(ops[1].inputs["b"].data, b_data_expected))


@with_setup(flag_manager.setup, flag_manager.teardown)
def test_conv_scale_scale():
    for order_x, order_w in itertools.product(orders4, orders4):
        conv = Convolution2D('conv', {'ksize': (3, 3), 'stride': (1, 1), 'padding': (1, 1)})
        scale1 = AxiswiseScale('scale', {'axis': Axis.C})
        scale2 = AxiswiseScale('scale', {'axis': Axis.C})

        x = Variable([8, 7, 6, 5], OrderNHWC)
        x.change_axis_order(order_x)

        w_shape = [4, 3, 3, 5]
        w_size: int = np.prod(w_shape)
        w = ConstantVariable(np.arange(w_size).reshape(w_shape), OrderNHWC)
        w.change_axis_order(order_w)
        w_data = w.data.copy()
        h, = conv(x, w)

        s1_shape = [h.shape_dict[Axis.C]]
        s1_size: int = np.prod(s1_shape)
        s1 = ConstantVariable(np.arange(s1_size).reshape(s1_shape), OrderC)
        s1_data = s1.data.copy()
        h, = scale1(h, s1)

        s2_shape = [h.shape_dict[Axis.C]]
        s2_size: int = np.prod(s2_shape)
        s2 = ConstantVariable(np.arange(s2_size).reshape(s2_shape), OrderC)
        s2_data = s2.data.copy()
        y, = scale2(h, s2)

        graph = Graph([x], [y])

        graph, _ = AffineConcat().optimize(graph)

        expander = (None,) * order_w.axes_dict[Axis.N] + (Ellipsis,) + (None,) * (3 - order_w.axes_dict[Axis.N])
        w_data_expected = w_data * s1_data[expander] * s2_data[expander]

        ops = listup_operators(graph)
        assert len(ops) == 1 and isinstance(ops, Convolution2D)
        assert np.all(np.equal(w.data, w_data_expected))


@with_setup(flag_manager.setup, flag_manager.teardown)
def test_conv_bias_bias():
    for order_x, order_w in itertools.product(orders4, orders4):
        conv = Convolution2D('conv', {'ksize': (3, 3), 'stride': (1, 1), 'padding': (1, 1)})
        bias1 = AxiswiseBias('bias', {'axis': Axis.C})
        bias2 = AxiswiseBias('bias', {'axis': Axis.C})

        x = Variable([8, 7, 6, 5], OrderNHWC)
        x.change_axis_order(order_x)

        w_shape = [4, 3, 3, 5]
        w_size: int = np.prod(w_shape)
        w = ConstantVariable(np.arange(w_size).reshape(w_shape).copy(), OrderNHWC)
        w.change_axis_order(order_w)
        w_data = w.data.copy()
        h, = conv(x, w)

        b1_shape = [h.shape_dict[Axis.C]]
        b1_size: int = np.prod(b1_shape)
        b1 = ConstantVariable(np.arange(b1_size).reshape(b1_shape), OrderC)
        b1_data = b1.data.copy()
        h, = bias1(h, b1)

        b2_shape = [h.shape_dict[Axis.C]]
        b2_size: int = np.prod(b2_shape)
        b2 = ConstantVariable(np.arange(b2_size).reshape(b2_shape), OrderC)
        b2_data = b2.data.copy()
        y, = bias2(h, b2)

        graph = Graph([x], [y])

        graph, _ = AffineConcat().optimize(graph)

        w_data_expected = w_data
        b_data_expected = b1_data + b2_data

        ops = listup_operators(graph)
        assert len(ops) == 2 and isinstance(ops[0], Convolution2D) and isinstance(ops[1], AxiswiseBias)
        assert np.all(np.equal(ops[0].inputs["w"].data, w_data_expected))
        assert np.all(np.equal(ops[1].inputs["b"].data, b_data_expected))


@with_setup(flag_manager.setup, flag_manager.teardown)
def test_conv_scale_bias():
    for order_x, order_w in itertools.product(orders4, orders4):
        conv = Convolution2D('conv', {'ksize': (3, 3), 'stride': (1, 1), 'padding': (1, 1)})
        scale = AxiswiseScale('scale', {'axis': Axis.C})
        bias = AxiswiseBias('bias', {'axis': Axis.C})

        x = Variable([8, 7, 6, 5], OrderNHWC)
        x.change_axis_order(order_x)

        w_shape = [4, 3, 3, 5]
        w_size: int = np.prod(w_shape)
        w = ConstantVariable(np.arange(w_size).reshape(w_shape), OrderNHWC)
        w.change_axis_order(order_w)
        w_data = w.data.copy()
        h, = conv(x, w)

        s_shape = [h.shape_dict[Axis.C]]
        s_size: int = np.prod(s_shape)
        s = ConstantVariable(np.arange(s_size).reshape(s_shape), OrderC)
        s_data = s.data.copy()
        h, = scale(h, s)

        b_shape = [h.shape_dict[Axis.C]]
        b_size: int = np.prod(b_shape)
        b = ConstantVariable(np.arange(b_size).reshape(b_shape), OrderC)
        b_data = b.data.copy()
        y, = bias(h, b)

        graph = Graph([x], [y])

        graph, _ = AffineConcat().optimize(graph)

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
        conv = Convolution2D('conv', {'ksize': (3, 3), 'stride': (1, 1), 'padding': (1, 1)})
        bias = AxiswiseBias('bias', {'axis': Axis.C})
        scale = AxiswiseScale('scale', {'axis': Axis.C})

        x = Variable([8, 7, 6, 5], OrderNHWC)
        x.change_axis_order(order_x)

        w_shape = [4, 3, 3, 5]
        w_size: int = np.prod(w_shape)
        w = ConstantVariable(np.arange(w_size).reshape(w_shape), OrderNHWC)
        w.change_axis_order(order_w)
        w_data = w.data.copy()
        h, = conv(x, w)

        b_shape = [h.shape_dict[Axis.C]]
        b_size: int = np.prod(b_shape)
        b = ConstantVariable(np.arange(b_size).reshape(b_shape), OrderC)
        b_data = b.data.copy()
        h, = bias(h, b)

        s_shape = [h.shape_dict[Axis.C]]
        s_size: int = np.prod(s_shape)
        s = ConstantVariable(np.arange(s_size).reshape(s_shape), OrderC)
        s_data = s.data.copy()
        y, = scale(h, s)

        graph = Graph([x], [y])

        graph, _ = AffineConcat().optimize(graph)

        expander = (None,) * order_w.axes_dict[Axis.N] + (Ellipsis,) + (None,) * (3 - order_w.axes_dict[Axis.N])
        w_data_expected = w_data * s_data[expander]
        b_data_expected = b_data * s_data

        ops = listup_operators(graph)
        assert len(ops) == 2 and isinstance(ops[0], Convolution2D) and isinstance(ops[1], AxiswiseBias)
        assert np.all(np.equal(ops[0].inputs["w"].data, w_data_expected))
        assert np.all(np.equal(ops[1].inputs["b"].data, b_data_expected))
