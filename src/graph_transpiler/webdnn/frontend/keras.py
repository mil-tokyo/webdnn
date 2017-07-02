# -*- coding:utf-8 -*-

"""
Keras model -> Graph object converters
Assuming Keras 2.0.4

Currently, the system assumes the model is trained with "data_format" == "channels_last".
If this is not the case, Flatten layer which follows Convolution have to change the order of variable.
Convolution implementation is currently assuming variable is NHWC.
"""

from collections import defaultdict
from typing import List

import keras
import keras.backend as K
import numpy as np
import tensorflow as tf

from webdnn.frontend.converter import Converter
from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.operators.average_pooling_2d import AveragePooling2D
from webdnn.graph.operators.axiswise_bias import AxiswiseBias
from webdnn.graph.operators.axiswise_scale import AxiswiseScale
from webdnn.graph.operators.concat import Concat
from webdnn.graph.operators.convolution2d import Convolution2D
from webdnn.graph.operators.elementwise_sum import ElementwiseSum
from webdnn.graph.operators.embedding import Embedding
from webdnn.graph.operators.hard_sigmoid import HardSigmoid
from webdnn.graph.operators.linear import Linear
from webdnn.graph.operators.lstm import LSTM
from webdnn.graph.operators.max_pooling_2d import MaxPooling2D
from webdnn.graph.operators.reinterpret_axis import ReinterpretAxis
from webdnn.graph.operators.relu import Relu
from webdnn.graph.operators.reshape import Reshape
from webdnn.graph.operators.sigmoid import Sigmoid
from webdnn.graph.operators.softmax import Softmax
from webdnn.graph.operators.softplus import Softplus
from webdnn.graph.operators.softsign import Softsign
from webdnn.graph.operators.zero_padding_1d import ZeroPadding1D
from webdnn.graph.operators.zero_padding_2d import ZeroPadding2D
from webdnn.graph.order import OrderNC, OrderC, OrderCN, Order, OrderNCHW, OrderNHWC, OrderNTC, OrderNT, OrderHWCN
from webdnn.graph.placeholder import Placeholder
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable
from webdnn.util import console
from webdnn.util.misc import mul


def _to_list(x):
    return x if isinstance(x, (list, tuple)) else [x]


class KerasConverter(Converter[keras.layers.Layer]):
    """
    KerasConverter

    Args:
        batch_size: input batch size (default=1)

    """

    def __init__(self, batch_size: int = 1):
        self._input_index_dict = defaultdict(lambda: 0)
        self._output_index_dict = defaultdict(lambda: 0)
        self._placeholder_N = Placeholder(label='N', value=batch_size)

    def convert(self, model: keras.models.Model) -> Graph:
        """
        Convert kerasmodel into WebDNN IR Graph. Currently, only TensorFlow backend is supported.

        Args:
            model (`keras.models.Model`): keras model

        Returns:
            (:class:`~webdnn.graph.graph.Graph`): WebDNN IR Graph
        """
        for tf_tensor in model.inputs:
            # FIXME: this assumption about input tensors' order is too ugly.
            shape = [self._placeholder_N if d.value is None else d.value for d in tf_tensor.shape]
            order = OrderNC if len(shape) == 2 else OrderNHWC

            self.set_variable(tf_tensor, Variable(shape, order))

        for depth in sorted(list(model.nodes_by_depth.keys()), reverse=True):
            for node in model.nodes_by_depth[depth]:
                self.convert_operator(node.outbound_layer)

                # Check that all output tensors from current layer are converted into WebDNN Variable
                for tensor in node.output_tensors:
                    if not self.has_variable(tensor):
                        raise AssertionError(
                            f"[KerasConverter] {node.outbound_layer} outputs {tensor}, but it was not converted into "
                            f"WebDNN Variable by {self._handler_map[self.__class__.__name__][self.serialize_operator_type(node.outbound_layer)]}")

        inputs = _to_list(self.get_input_tensor(model))
        outputs = _to_list(self.get_output_tensor(model))
        return Graph([self.get_variable(t) for t in inputs], [self.get_variable(t) for t in outputs])

    def convert_to_constant_variable(self, tf_var: tf.Variable, order: Order) -> ConstantVariable:
        """
        Convert TensorFlow variable (parameter of kerasmodel) into
        :class:`~webdnn.graph.variables.constant_variable.ConstantVariable`.

        This method also registers the mapping information between TensorFlow variable and WebDNN constant variable.
        If specified TensorFlow variable is already registered into converter, converter checks that the shape and order
        is valid

        *This method is provided only for implementing custom converter handler.*

        Args:
            tf_var (tensorflow.Variable): TensorFlow variable
            order: (:class:`~webdnn.graph.order.Order`) data order

        Returns:
            (:class:`~webdnn.graph.variables.constant_variable.ConstantVariable`): converted variable.
        """
        data = K.batch_get_value([tf_var])[0]

        if self.has_variable(tf_var):
            variable = self.get_variable(tf_var)
            assert variable.shape == list(data.shape), f"[KerasConverter] {tf_var} is already registered before, and " \
                                                       f"shape mismatch is detected: (registered shape)=" \
                                                       f"{variable.shape}, (given tensorflow variable's shape)=" \
                                                       f"{data.shape}"
            assert variable.order == order, f"[KerasConverter] {tf_var} is already registered before, and order " \
                                            f"mismatch is detected: (registered order)={variable.order}, (given " \
                                            f"tensorflow variable's order)={order}"

        else:
            variable = ConstantVariable(data, order)
            self.set_variable(tf_var, variable)

        return variable

    def get_input_tensor(self, k_op: keras.layers.Layer) -> List[tf.Tensor]:
        """
        Return input tensor(s) of specified keras layer.

        KerasConverter has counters about how many times this method is called for each keras operator, and at first time.
        this method returns first input tensors (= `k_op.get_input_at(0)`), and when call this method again, this method
        returns second input tensors (= `k_op.get_input_at(1)`). Therefore, you should call this method just once in your
        converter handler.

        *This method is provided only for implementing custom converter handler.*

        Args:
            k_op (keras.layers.Layer): keras operator

        Returns:
            (list of tensorflow.Tensor): list of input tensor(s). Even if only one element, it's wrapped in a list.
        """
        index = self._input_index_dict[k_op]
        self._input_index_dict[k_op] += 1
        return _to_list(k_op.get_input_at(index))

    def get_output_tensor(self, k_op: keras.layers.Layer) -> List[tf.Tensor]:
        """
        Return output tensor(s) of specified keras layer.

        KerasConverter has counters about how many times this method is called for each keras operator, and at first time.
        this method returns first output tensors (= `k_op.get_output_at(0)`), and when call this method again, this method
        returns second output tensors (= `k_op.get_output_at(1)`). Therefore, you should call this method just once in your
        converter handler.

        *This method is provided only for implementing custom converter handler.*

        Args:
            k_op (keras.layers.Layer): keras operator

        Returns:
            (list of tensorflow.Tensor): list of output tensor(s). Even if only one element, it's wrapped in a list.
        """
        index = self._output_index_dict[k_op]
        self._output_index_dict[k_op] += 1
        return _to_list(k_op.get_output_at(index))


def do_activation(activation: any, x: Variable) -> Variable:
    if activation is keras.activations.relu:
        return Relu(None)(x)[0]

    elif activation is keras.activations.sigmoid:
        return Sigmoid(None)(x)[0]

    elif activation is keras.activations.hard_sigmoid:
        return HardSigmoid(None)(x)[0]

    elif activation is keras.activations.softplus:
        return Softplus(None, beta=1.0)(x)[0]

    elif activation is keras.activations.softsign:
        return Softsign(None)(x)[0]

    elif activation is keras.activations.softmax:
        return Softmax(None, axis=x.order.axes[-1])(x)[0]

    elif activation is keras.activations.linear:
        return x

    else:
        raise NotImplementedError(f"[KerasConverter] Unknown activation: {activation}")


@KerasConverter.register_handler("Model")
@KerasConverter.register_handler("Sequential")
def _convert_model(converter: KerasConverter, k_op: keras.models.Model):
    graph = converter.convert(k_op)

    # Initial state of nested model
    #
    #    Global Model : [layer] -> tensor(A) -> [...........Model..........] -> tensor(C) -> [layer] ->
    #                 :
    #     Local Model :            tensor(B) -> [layer] -> tensor -> [layer] -> tensor(D)
    #

    # 1. Replace local input variable (converted from tensor(B)) into global input variable (converted from tensor(A))
    #
    #    Global Model : [layer] -> tensor(A) -> [...........Model..........] -> tensor(C) -> [layer] ->
    #                 :             |
    #     Local Model :             +---------> [layer] -> tensor -> [layer] -> tensor(D)
    #
    global_inputs = [converter.get_variable(tensor) for tensor in converter.get_input_tensor(k_op)]
    for global_variable, local_variable in zip(global_inputs, graph.inputs):
        local_variable.replace(global_variable)

    # 2. Register local output variable (converted from tensor(D)) as the variable converted from tensor(C)
    #
    #    Global Model : [layer] -> tensor(A)                                     +---------> [layer] ->
    #                 :             |                                            |
    #     Local Model :             +---------> [layer] -> tensor -> [layer] -> tensor(D)
    #
    global_outputs = _to_list(converter.get_output_tensor(k_op))
    for global_tensor, local_variable in zip(global_outputs, graph.outputs):
        converter.set_variable(global_tensor, local_variable)


# noinspection PyUnusedLocal
@KerasConverter.register_handler("InputLayer")
def _convert_input_layer(converter: KerasConverter, k_op: keras.layers.InputLayer):
    pass


@KerasConverter.register_handler("Dense")
def _convert_dense(converter: KerasConverter, k_op: keras.layers.Dense):
    x = converter.get_variable(converter.get_input_tensor(k_op)[0])
    w = converter.convert_to_constant_variable(k_op.kernel, OrderCN)
    y, = Linear(None)(x, w)

    if k_op.use_bias:
        b = converter.convert_to_constant_variable(k_op.bias, OrderC)
        y, = AxiswiseBias(None, Axis.C)(y, b)

    y = do_activation(k_op.activation, y)
    converter.set_variable(converter.get_output_tensor(k_op)[0], y)


@KerasConverter.register_handler("Dropout")
def _convert_dropout(converter: KerasConverter, k_op: keras.layers.Dropout):
    console.warning("[KerasConverter] omitting dropout")

    x = converter.get_variable(converter.get_input_tensor(k_op)[0])
    y = x
    converter.set_variable(converter.get_output_tensor(k_op)[0], y)


@KerasConverter.register_handler("Conv2D")
def _convert_conv2d(converter: KerasConverter, k_op: keras.layers.Conv2D):
    x = converter.get_variable(converter.get_input_tensor(k_op)[0])

    if k_op.data_format == "channels_first":
        assert x.order == OrderNCHW

    elif k_op.data_format == "channels_last":
        assert x.order == OrderNHWC

    else:
        raise ValueError(f"[KerasConverter] Unknown data format is detected: {k_op.data_format}")

    w = converter.convert_to_constant_variable(k_op.kernel, OrderHWCN)

    ksize = tuple(k_op.kernel_size)
    stride = tuple(k_op.strides)
    dilation_rate = tuple(k_op.dilation_rate)
    if k_op.padding == "valid":
        padding = (0, 0)

    elif k_op.padding == "same":
        padding = (ksize[0] // 2, ksize[1] // 2)

    else:
        raise ValueError(f"[KerasConverter] Unknown padding: {k_op.padding}")

    y, = Convolution2D(None, ksize=ksize, stride=stride, padding=padding, dilation_rate=dilation_rate)(x, w)

    if k_op.use_bias:
        b = converter.convert_to_constant_variable(k_op.bias, OrderC)
        y, = AxiswiseBias(None, Axis.C)(y, b)

    y = do_activation(k_op.activation, y)
    converter.set_variable(converter.get_output_tensor(k_op)[0], y)


@KerasConverter.register_handler("MaxPooling2D")
def _convert_max_pooling2d(converter: KerasConverter, k_op: keras.layers.MaxPooling2D):
    x = converter.get_variable(converter.get_input_tensor(k_op)[0])

    if k_op.data_format == "channels_first":
        assert x.order == OrderNCHW

    elif k_op.data_format == "channels_last":
        assert x.order == OrderNHWC

    else:
        raise ValueError(f"[KerasConverter] Unknown data format: {k_op.data_format}")

    ksize = tuple(k_op.pool_size)
    stride = tuple(k_op.strides)
    if k_op.padding == "valid":
        padding = (0, 0)

    elif k_op.padding == "same":
        padding = (ksize[0] // 2, ksize[1] // 2)

    else:
        raise ValueError(f"[KerasConverter] Unknown padding: {k_op.padding}")

    y, = MaxPooling2D(None, ksize=ksize, stride=stride, padding=padding)(x)
    converter.set_variable(converter.get_output_tensor(k_op)[0], y)


@KerasConverter.register_handler("AveragePooling2D")
def _convert_max_pooling2d(converter: KerasConverter, k_op: keras.layers.AveragePooling2D):
    x = converter.get_variable(converter.get_input_tensor(k_op)[0])

    if k_op.data_format == "channels_first":
        assert x.order == OrderNCHW

    elif k_op.data_format == "channels_last":
        assert x.order == OrderNHWC

    else:
        raise ValueError(f"[KerasConverter] Unknown data format: {k_op.data_format}")

    ksize = tuple(k_op.pool_size)
    stride = tuple(k_op.strides)
    if k_op.padding == "valid":
        padding = (0, 0)

    elif k_op.padding == "same":
        padding = (ksize[0] // 2, ksize[1] // 2)

    else:
        raise ValueError(f"[KerasConverter] Unknown padding: {k_op.padding}")

    y, = AveragePooling2D(None, ksize=ksize, stride=stride, padding=padding)(x)
    converter.set_variable(converter.get_output_tensor(k_op)[0], y)


@KerasConverter.register_handler("GlobalAveragePooling2D")
def convert_layer_global_average_pooling2d(converter: KerasConverter, k_op: keras.layers.GlobalAveragePooling2D):
    x = converter.get_variable(converter.get_input_tensor(k_op)[0])
    if k_op.data_format == "channels_first":
        assert x.order == OrderNCHW

    elif k_op.data_format == "channels_last":
        assert x.order == OrderNHWC

    else:
        raise ValueError(f"[KerasConverter] Unknown data format: {k_op.data_format}")

    y, = AveragePooling2D(None, ksize=(x.shape_dict[Axis.H], x.shape_dict[Axis.W]), stride=(1, 1), padding=(0, 0))(x)

    # flatten without changing memory layout
    z, = Reshape(None, in_order=y.order, out_order=OrderNC, out_shape=[y.shape[0], mul(y.shape[1:])])(y)
    converter.set_variable(converter.get_output_tensor(k_op)[0], z)


@KerasConverter.register_handler("Flatten")
def _convert_flatten(converter: KerasConverter, k_op: keras.layers.Flatten):
    x = converter.get_variable(converter.get_input_tensor(k_op)[0])

    # flatten without changing memory layout
    y, = Reshape(None, in_order=x.order, out_order=OrderNC, out_shape=[x.shape[0], mul(x.shape[1:])])(x)
    converter.set_variable(converter.get_output_tensor(k_op)[0], y)


@KerasConverter.register_handler("Concatenate")
def _convert_concatenate(converter: KerasConverter, k_op: keras.layers.Concatenate):
    xs = [converter.get_variable(tensor) for tensor in converter.get_input_tensor(k_op)]
    axis = xs[0].order.axes[k_op.axis]

    y, = Concat(None, axis=axis)(*xs)
    converter.set_variable(converter.get_output_tensor(k_op)[0], y)


@KerasConverter.register_handler("Add")
def _convert_add(converter: KerasConverter, k_op: keras.layers.Add):
    xs = [converter.get_variable(tensor) for tensor in converter.get_input_tensor(k_op)]

    y, = ElementwiseSum(None)(*xs)
    converter.set_variable(converter.get_output_tensor(k_op)[0], y)


@KerasConverter.register_handler("Activation")
def _convert_activation(converter: KerasConverter, k_op: keras.layers):
    y = converter.get_variable(converter.get_input_tensor(k_op)[0])

    y = do_activation(k_op.activation, y)
    converter.set_variable(converter.get_output_tensor(k_op)[0], y)


@KerasConverter.register_handler("BatchNormalization")
def _convert_batch_normalization(converter: KerasConverter, k_op: keras.layers.BatchNormalization):
    x = converter.get_variable(converter.get_input_tensor(k_op)[0])

    axis = x.order.axes[k_op.axis]

    variance_data, mean_data = K.batch_get_value([k_op.moving_variance, k_op.moving_mean])

    if k_op.scale:
        gamma_data, = K.batch_get_value([k_op.gamma])
    else:
        gamma_data = np.ones_like(variance_data)

    if k_op.center:
        beta_data, = K.batch_get_value([k_op.beta])
    else:
        beta_data = np.zeros_like(mean_data)

    gamma_div_std_data = gamma_data / np.sqrt(variance_data + k_op.epsilon)
    beta_scaled_data = beta_data - mean_data * gamma_div_std_data

    gamma_div_std = ConstantVariable(gamma_div_std_data, Order([axis]))
    beta_scaled = ConstantVariable(beta_scaled_data, Order([axis]))

    y, = AxiswiseScale(None, axis=axis)(x, gamma_div_std)
    y, = AxiswiseBias(None, axis=axis)(y, beta_scaled)
    converter.set_variable(converter.get_output_tensor(k_op)[0], y)


@KerasConverter.register_handler("ZeroPadding2D")
def _convert_zero_padding2d(converter: KerasConverter, k_op: keras.layers.ZeroPadding2D):
    x = converter.get_variable(converter.get_input_tensor(k_op)[0])

    padding = k_op.padding
    top = padding[0][0]
    if top != padding[0][1]:
        raise ValueError("Padding size of top and bottom must be same.")

    left = padding[1][0]
    if left != padding[1][1]:
        raise ValueError("Padding size of left and right must be same.")

    y, = ZeroPadding2D(None, (top, left))(x)
    converter.set_variable(converter.get_output_tensor(k_op)[0], y)


@KerasConverter.register_handler("ZeroPadding1D")
def _convert_zero_padding1d(converter: KerasConverter, k_op: keras.layers.ZeroPadding1D):
    x = converter.get_variable(converter.get_input_tensor(k_op)[0])

    assert x.order == OrderNTC
    if k_op.padding[0][0] != k_op.padding[0][1]:
        raise ValueError("Padding size of left and right must be same.")

    y, = ZeroPadding1D(None, padding=tuple(k_op.padding))(x)
    converter.set_variable(converter.get_output_tensor(k_op)[0], y)


@KerasConverter.register_handler("Embedding")
def _convert_embedding(converter: KerasConverter, k_op: keras.layers.Embedding):
    x = converter.get_variable(converter.get_input_tensor(k_op)[0])

    if x.order == OrderNC:
        x, = ReinterpretAxis(None, in_order=OrderNC, out_order=OrderNT)(x)

    w = converter.convert_to_constant_variable(k_op.embeddings, OrderCN)

    y, = Embedding(None)(x, w)
    converter.set_variable(converter.get_output_tensor(k_op)[0], y)


@KerasConverter.register_handler("LSTM")
def _convert_lstm(converter: KerasConverter, k_op: keras.layers.LSTM):
    assert k_op.stateful is False, "[KerasConverter] Currently, LSTM.stateful is not supported"
    assert k_op.go_backwards is False, "[KerasConverter] Currently, LSTM.go_backwards is not supported"

    x = converter.get_variable(converter.get_input_tensor(k_op)[0])
    w_input = converter.convert_to_constant_variable(k_op.kernel, OrderCN)
    w_hidden = converter.convert_to_constant_variable(k_op.recurrent_kernel, OrderCN)

    if k_op.use_bias:
        b = converter.convert_to_constant_variable(k_op.bias, OrderC)

    else:
        b = None

    y, = LSTM(None, k_op.use_bias, k_op.return_sequences,
              use_initial_c=False, use_initial_h=False,
              activation=k_op.activation,
              recurrent_activation=k_op.recurrent_activation)(x, w_input, w_hidden, b)
    converter.set_variable(converter.get_output_tensor(k_op)[0], y)
