# -*- coding:utf-8 -*-

"""
Keras model -> Graph object converters
Assuming Keras 2.0.4

Currently, the system assumes the model is trained with "data_format" == "channels_last".
If this is not the case, Flatten layer which follows Convolution have to change the order of variable.
Convolution implementation is currently assuming variable is NHWC.
"""

from typing import List, Tuple, Dict

import h5py
import keras
import numpy as np
import tensorflow as tf

from webdnn.frontend.converter import Converter
from webdnn.graph import traverse
from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.operators.average_pooling_2d import AveragePooling2D
from webdnn.graph.operators.axiswise_bias import AxiswiseBias
from webdnn.graph.operators.axiswise_scale import AxiswiseScale
from webdnn.graph.operators.concat import Concat
from webdnn.graph.operators.convolution2d import Convolution2D
from webdnn.graph.operators.elementwise_sum import ElementwiseSum
from webdnn.graph.operators.embedding import Embedding
from webdnn.graph.operators.linear import Linear
from webdnn.graph.operators.lstm import LSTM
from webdnn.graph.operators.max_pooling_2d import MaxPooling2D
from webdnn.graph.operators.reinterpret_axis import ReinterpretAxis
from webdnn.graph.operators.reshape import Reshape
from webdnn.graph.operators.zero_padding_2d import ZeroPadding2D
from webdnn.graph.order import OrderNC, OrderC, OrderCN, OrderHWCN, \
    OrderNT
from webdnn.graph.placeholder import Placeholder
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable
from webdnn.util import console
from webdnn.util.misc import mul


def _convert_shape(shape: tf.TensorShape):
    return [Placeholder(label="N") if d.value is None else d.value for d in shape]  # type: tf.Dimension


class KerasConverter(Converter[keras.layers.Layer]):
    _weight_dataset: h5py.Group
    _global_input_variables: List[Variable]
    _global_output_variables: List[Variable]
    _variable_table_stack = List[Dict[object, Variable]]
    _container_name_stack = List[str]
    _constant_variables: Dict[str, ConstantVariable]

    def convert(self, model: keras.models.Model) -> Graph:
        for layer in model.layers:
            self.convert_operator(layer)

        graph = Graph([self.get_variable(t) for t in model.inputs],
                      [self.get_variable(t) for t in model.outputs])

        return graph


# def do_activation(activation_type: str, x: Variable) -> Variable:
#     act_opr = None
#     if activation_type == "relu":
#         act_opr = Relu(None)
#     elif activation_type == "sigmoid":
#         act_opr = Sigmoid(None)
#     elif activation_type == "hard_sigmoid":
#         act_opr = HardSigmoid(None)
#     elif activation_type == "softplus":
#         act_opr = Softplus(None, beta=1.0)
#     elif activation_type == "softsign":
#         act_opr = Softsign(None)
#     elif activation_type == "softmax":
#         act_opr = Softmax(None, axis=x.order.axes[-1])
#     elif activation_type == "linear":
#         pass
#     else:
#         raise NotImplementedError(f"Unknown activation {activation_type}")
#
#     if act_opr is not None:
#         x, = act_opr(x)
#
#     return x


@KerasConverter.register_handler("InputLayer")
def _convert_input_layer(converter: KerasConverter, operator: keras.layers.InputLayer):
    """
    Dummy layer
    Args:
        converter:
        operator:

    Returns:

    """
    pass


@KerasConverter.register_handler("Dense")
def _convert_dense(converter: KerasConverter, operator: keras.layers.Dense):
    if converter.has_variable(operator.input):
        x = converter.get_variable(operator.input)  # type: tf.Tensor
    else:
        x = Variable(_convert_shape(operator.input.shape), OrderNC)
        converter.set_variable(operator.input, x)

    if converter.has_variable(operator.weights[0].value()):
        w = converter.get_variable(operator.weights[0].value())  # type: tf.Tensor
    else:
        w = ConstantVariable(operator.get_weights()[0], OrderCN)
        converter.set_variable(operator.weights[0].value(), w)

    if converter.has_variable(operator.output):
        y = converter.get_variable(operator.output)  # type: tf.Tensor
    else:
        y = Variable(_convert_shape(operator.output.shape), OrderNC)
        converter.set_variable(operator.output, y)

    linear = Linear(None)
    dummy_y, = linear(x, w)

    if operator.use_bias:
        if converter.has_variable(operator.weights[1].value()):
            b = converter.get_variable(operator.weights[1].value())  # type: tf.Tensor
        else:
            b = ConstantVariable(operator.get_weights()[1], OrderC)
            converter.set_variable(operator.weights[1].value(), b)

        dummy_y, = AxiswiseBias(None, axis=Axis.C)(dummy_y, b)

    dummy_y.replace(y)


@KerasConverter.register_handler("Dropout")
def _convert_dropout(converter: KerasConverter, operator: keras.layers.Dropout):
    x = operator.inputs[0]
    console.warning("[KerasConverter] omitting dropout")

    operator.outputs = [x]


@KerasConverter.register_handler("Conv2D")
def _convert_conv2d(converter: KerasConverter, operator: keras.layers.Convolution2D):
    """
    Example:
       {'class_name': 'Conv2D',
'config': {'activation': 'relu',
'activity_regularizer': None,
'bias_constraint': None,
'bias_initializer': {'class_name': 'Zeros', 'config': {}},
'bias_regularizer': None,
'data_format': 'channels_last',
'dilation_rate': [1, 1],
'filters': 64,
'kernel_constraint': None,
'kernel_initializer': {'class_name': 'VarianceScaling',
 'config': {'distribution': 'uniform',
  'mode': 'fan_avg',
  'scale': 1.0,
  'seed': None}},
'kernel_regularizer': None,
'kernel_size': [3, 3],
'name': 'conv2d_2',
'padding': 'valid',
'strides': [1, 1],
'trainable': True,
'use_bias': True}},
    :param layer_config:
    :param inputs:
    :return:
    """
    assert len(operator.inputs) == 1
    x = operator.inputs[0]
    assert operator.specific_config["data_format"] == "channels_last"
    w = converter.create_constant_variable(operator, "kernel:0", OrderHWCN)  # order does not depend on data_format
    ksize: Tuple[int, int] = tuple(operator.specific_config["kernel_size"])
    stride: Tuple[int, int] = tuple(operator.specific_config["strides"])
    dilation_rate: Tuple[int, int] = tuple(operator.specific_config.get("dilation_rate", 1))
    padding_keras: str = operator.specific_config["padding"]  # valid or same
    if padding_keras == "valid":
        padding = (0, 0)
    elif padding_keras == "same":
        padding = (ksize[0] // 2, ksize[1] // 2)
    else:
        raise ValueError("Unknown padding")

    conv2d_opr = Convolution2D(None,
                               ksize=ksize,
                               stride=stride,
                               padding=padding,
                               dilation_rate=dilation_rate)
    y, = conv2d_opr(x, w)

    if operator.specific_config["use_bias"]:
        bias = converter.create_constant_variable(operator, "bias:0", OrderC)
        bias_opr = AxiswiseBias(None, Axis.C)
        y, = bias_opr(y, bias)

    y = do_activation(operator.specific_config["activation"], y)

    operator.outputs = [y]


@KerasConverter.register_handler("MaxPooling2D")
def _convert_max_pooling2d(converter: KerasConverter, operator: keras.layers.MaxPooling2D):
    """
    Example:
          {'class_name': 'MaxPooling2D',
   'config': {'data_format': 'channels_last',
    'name': 'max_pooling2d_1',
    'padding': 'valid',
    'pool_size': [2, 2],
    'strides': [2, 2],
    'trainable': True}},
    """
    assert len(operator.inputs) == 1
    x = operator.inputs[0]
    ksize: Tuple[int, int] = tuple(operator.specific_config["pool_size"])
    stride: Tuple[int, int] = tuple(operator.specific_config["strides"])
    padding_keras: str = operator.specific_config["padding"]  # valid or same
    if padding_keras == "valid":
        padding = (0, 0)
    elif padding_keras == "same":
        padding = (ksize[0] // 2, ksize[1] // 2)
    else:
        raise ValueError("Unknown padding")

    max_pooling_2d_opr = MaxPooling2D(None,
                                      ksize=ksize,
                                      stride=stride,
                                      padding=padding)
    y, = max_pooling_2d_opr(x)

    operator.outputs = [y]


@KerasConverter.register_handler("AveragePooling2D")
def convert_layer_average_pooling2d(converter: KerasConverter, operator: keras.layers.AveragePooling2D):
    """
    Example:
{'class_name': 'AveragePooling2D',
'config': {'data_format': 'channels_last',
'name': 'avg_pool',
'padding': 'valid',
'pool_size': [7, 7],
'strides': [7, 7],
'trainable': True},
'inbound_nodes': [[['activation_49', 0, 0, {}]]],
'name': 'avg_pool'},

    :param layer_config:
    :param inputs:
    :return:
    """

    assert len(operator.inputs) == 1
    x = operator.inputs[0]
    ksize: Tuple[int, int] = tuple(operator.specific_config["pool_size"])
    stride: Tuple[int, int] = tuple(operator.specific_config["strides"])
    padding_keras: str = operator.specific_config["padding"]  # valid or same
    if padding_keras == "valid":
        padding = (0, 0)
    elif padding_keras == "same":
        padding = (ksize[0] // 2, ksize[1] // 2)
    else:
        raise ValueError("Unknown padding")

    average_pooling_2d_opr = AveragePooling2D(None,
                                              ksize=ksize,
                                              stride=stride,
                                              padding=padding)
    y, = average_pooling_2d_opr(x)

    operator.outputs = [y]


@KerasConverter.register_handler("GlobalAveragePooling2D")
def convert_layer_global_average_pooling2d(converter: KerasConverter, operator: keras.layers.GlobalAveragePooling2D):
    """
    Example:
      {'class_name': 'GlobalAveragePooling2D',
'config': {'data_format': 'channels_last',
 'name': 'global_average_pooling2d_1',
 'trainable': True},
'inbound_nodes': [[['add_2', 0, 0, {}]]],
'name': 'global_average_pooling2d_1'},

    :param layer_config:
    :param inputs:
    :return:
    """

    assert len(operator.inputs) == 1
    x = operator.inputs[0]

    ksize: Tuple[int, int] = (x.shape_dict[Axis.H], x.shape_dict[Axis.W])
    average_pooling_2d_opr = AveragePooling2D(None,
                                              ksize=ksize,
                                              stride=(1, 1),
                                              padding=(0, 0))
    y, = average_pooling_2d_opr(x)

    # flatten without changing memory layout
    reshape_opr = Reshape(None, in_order=y.order, out_order=OrderNC, out_shape=[y.shape[0], mul(y.shape[1:])])
    z, = reshape_opr(y)

    operator.outputs = [z]


@KerasConverter.register_handler("Flatten")
def _convert_flatten(converter: KerasConverter, operator: keras.layers.Flatten):
    """
    Example:
      {'class_name': 'Flatten',
'config': {'name': 'flatten_1', 'trainable': True}},

    :param layer_config:
    :param inputs:
    :return:
    """
    assert len(operator.inputs) == 1
    x = operator.inputs[0]
    assert x.order.axes[0] == Axis.N
    reshape_opr = Reshape(None, in_order=x.order, out_order=OrderNC, out_shape=[x.shape[0], mul(x.shape[1:])])
    y, = reshape_opr(x)

    operator.outputs = [y]


@KerasConverter.register_handler("Concatenate")
def _convert_concatenate(converter: KerasConverter, operator: keras.layers.Concatenate):
    """
    Example:
      {'name': 'mixed0', 'trainable': True, 'axis': 3}

    :param layer_config:
    :param inputs:
    :return:
    """
    xs = operator.inputs
    axis = xs[0].order.axes[operator.specific_config["axis"]]
    concat_opr = Concat(None, axis=axis)
    y, = concat_opr(*xs)

    operator.outputs = [y]


@KerasConverter.register_handler("Add")
def _convert_add(converter: KerasConverter, operator: keras.layers.Add):
    """
    Example:
          {'class_name': 'Add',
    'config': {'name': 'add_1', 'trainable': True},
    'inbound_nodes': [[['conv2d_2', 0, 0, {}], ['conv2d_3', 0, 0, {}]]],
    'name': 'add_1'},
    :param layer_config:
    :param inputs:
    :return:
    """
    xs = operator.inputs
    sum_opr = ElementwiseSum(None)
    y, = sum_opr(*xs)

    operator.outputs = [y]


@KerasConverter.register_handler("Activation")
def _convert_activation(converter: KerasConverter, operator: keras.layers.Activation):
    assert len(operator.inputs) == 1
    y = operator.inputs[0]

    y = do_activation(operator.specific_config["activation"], y)

    operator.outputs = [y]


@KerasConverter.register_handler("BatchNormalization")
def _convert_batch_normalization(converter: KerasConverter, operator: keras.layers.BatchNormalization):
    """
    Example:
{'class_name': 'BatchNormalization',
'config': {'axis': 3,
'beta_constraint': None,
'beta_initializer': {'class_name': 'Zeros', 'config': {}},
'beta_regularizer': None,
'center': True,
'epsilon': 0.001,
'gamma_constraint': None,
'gamma_initializer': {'class_name': 'Ones', 'config': {}},
'gamma_regularizer': None,
'momentum': 0.99,
'moving_mean_initializer': {'class_name': 'Zeros', 'config': {}},
'moving_variance_initializer': {'class_name': 'Ones', 'config': {}},
'name': 'bn2a_branch2a',
'scale': True,
'trainable': True},
'inbound_nodes': [[['res2a_branch2a', 0, 0, {}]]],
'name': 'bn2a_branch2a'},

    :param layer_config:
    :param inputs:
    :return:
    """
    assert len(operator.inputs) == 1
    x = operator.inputs[0]

    axis = x.order.axes[operator.specific_config["axis"]]
    mean = converter.create_constant_array(operator, "moving_mean:0")
    variance = converter.create_constant_array(operator, "moving_variance:0")

    if operator.specific_config["scale"]:
        gamma = converter.create_constant_array(operator, "gamma:0")
    else:
        gamma = np.ones_like(variance)

    if operator.specific_config["center"]:
        beta = converter.create_constant_array(operator, "beta:0")
    else:
        beta = np.ones_like(variance)

    gamma_div_std = gamma / np.sqrt(variance + operator.specific_config["epsilon"])
    beta_scaled = beta - mean * gamma_div_std

    scale_opr = AxiswiseScale(None, axis=axis)
    bias_opr = AxiswiseBias(None, axis=axis)
    scale_out, = scale_opr(x, ConstantVariable(gamma_div_std, OrderC))
    y, = bias_opr(scale_out, ConstantVariable(beta_scaled, OrderC))

    operator.outputs = [y]


@KerasConverter.register_handler("ZeroPadding2D")
def _convert_zero_padding2d(converter: KerasConverter, operator: keras.layers.ZeroPadding2D):
    """
    Example:
 {'class_name': 'ZeroPadding2D',
  'config': {'data_format': 'channels_last',
   'name': 'zero_padding2d_1',
   'padding': [[3, 3], [3, 3]],
   'trainable': True},
  'inbound_nodes': [[['input_1', 0, 0, {}]]],
  'name': 'zero_padding2d_1'},
    :param layer_config:
    :param inputs:
    :return:
    """
    assert len(operator.inputs) == 1
    x = operator.inputs[0]

    padding = operator.specific_config["padding"]
    top = padding[0][0]
    if top != padding[0][1]:
        raise ValueError("Padding size of top and bottom must be same.")
    left = padding[1][0]
    if left != padding[1][1]:
        raise ValueError("Padding size of left and right must be same.")

    pad_opr = ZeroPadding2D(None, (top, left))
    y, = pad_opr(x)

    operator.outputs = [y]


@KerasConverter.register_handler("Embedding")
def _convert_embedding(converter: KerasConverter, operator: keras.layers.Embedding):
    """
    {'class_name': 'Embedding',
   'config': {'activity_regularizer': None,
    'batch_input_shape': [None, None],
    'dtype': 'int32',
    'embeddings_constraint': None,
    'embeddings_initializer': {'class_name': 'RandomUniform',
     'config': {'maxval': 0.05, 'minval': -0.05, 'seed': None}},
    'embeddings_regularizer': None,
    'input_dim': 20000,
    'input_length': None,
    'mask_zero': False,
    'name': 'embedding_1',
    'output_dim': 128,
    'trainable': True}}

    Args:
        converter:
        operator:

    Returns:

    """
    assert len(operator.inputs) == 1
    x = operator.inputs[0]
    if x.order == OrderNC:
        # re-interpret as NT
        reinterpret_opr = ReinterpretAxis(None, in_order=OrderNC, out_order=OrderNT)
        x, = reinterpret_opr(x)
    w = converter.create_constant_variable(operator, "embeddings:0", OrderCN)
    embedding_opr = Embedding(None)

    y, = embedding_opr(x, w)

    operator.outputs = [y]


@KerasConverter.register_handler("LSTM")
def _convert_lstm(converter: KerasConverter, operator: keras.layers.LSTM):
    """
    {'class_name': 'LSTM',
   'config': {'activation': 'tanh',
    'activity_regularizer': None,
    'bias_constraint': None,
    'bias_initializer': {'class_name': 'Zeros', 'config': {}},
    'bias_regularizer': None,
    'dropout': 0.2,
    'go_backwards': False,
    'implementation': 0,
    'kernel_constraint': None,
    'kernel_initializer': {'class_name': 'VarianceScaling',
     'config': {'distribution': 'uniform',
      'mode': 'fan_avg',
      'scale': 1.0,
      'seed': None}},
    'kernel_regularizer': None,
    'name': 'lstm_1',
    'recurrent_activation': 'hard_sigmoid',
    'recurrent_constraint': None,
    'recurrent_dropout': 0.2,
    'recurrent_initializer': {'class_name': 'Orthogonal',
     'config': {'gain': 1.0, 'seed': None}},
    'recurrent_regularizer': None,
    'return_sequences': False,
    'stateful': False,
    'trainable': True,
    'unit_forget_bias': True,
    'units': 128,
    'unroll': False,
    'use_bias': True}}

    Args:
        converter:
        operator:

    Returns:

    """
    assert len(operator.inputs) == 1
    assert operator.specific_config["activation"] == "tanh"
    assert operator.specific_config["recurrent_activation"] == "hard_sigmoid"
    assert operator.specific_config["stateful"] is False
    assert operator.specific_config["go_backwards"] is False
    x = operator.inputs[0]
    w_input = converter.create_constant_variable(operator, "kernel:0", OrderCN)
    w_hidden = converter.create_constant_variable(operator, "recurrent_kernel:0", OrderCN)
    if operator.specific_config["use_bias"]:
        b = converter.create_constant_variable(operator, "bias:0", OrderC)
    else:
        b = None
    lstm_opr = LSTM(None, operator.specific_config["use_bias"], operator.specific_config["return_sequences"], False)

    y, _ = lstm_opr(x, w_input, w_hidden, b)

    operator.outputs = [y]
