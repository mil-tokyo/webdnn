# -*- coding:utf-8 -*-

"""
Keras model -> Graph object converters
Assuming Keras 2.0.4

Currently, the system assumes the model is trained with "data_format" == "channels_last".
If this is not the case, Flatten layer which follows Convolution have to change the order of variable.
Convolution implementation is currently assuming variable is NHWC.
"""

from typing import List, Tuple, Dict, Type

import json
from warnings import warn

import numpy as np
import h5py

from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.operator import Operator
from webdnn.graph.converters.converter import Converter
from webdnn.graph.operators.average_pooling_2d import AveragePooling2D
from webdnn.graph.operators.axiswise_bias import AxiswiseBias
from webdnn.graph.operators.axiswise_scale import AxiswiseScale
from webdnn.graph.operators.concat import Concat
from webdnn.graph.operators.convolution2d import Convolution2D
from webdnn.graph.operators.deconvolution2d import Deconvolution2D
from webdnn.graph.operators.elementwise_sum import ElementwiseSum
from webdnn.graph.operators.elu import Elu
from webdnn.graph.operators.flatten import Flatten
from webdnn.graph.operators.linear import Linear
from webdnn.graph.operators.local_response_normalization import LocalResponseNormalization
from webdnn.graph.operators.max_pooling_2d import MaxPooling2D
from webdnn.graph.operators.relu import Relu
from webdnn.graph.operators.scalar_affine import ScalarAffine
from webdnn.graph.operators.tanh import Tanh
from webdnn.graph.order import OrderNC, OrderNCHW, OrderC, OrderCN, OrderHWNC, OrderHWCN, \
    OrderNHWC, OrderCNHW, OrderCHWN, Order
from webdnn.graph.variable import Variable
from webdnn.graph.variables.attributes.input import Input
from webdnn.graph.variables.attributes.output import Output
from webdnn.graph.variables.constant_variable import ConstantVariable


class KerasOperator:
    class_name: str
    name: str
    serial_index: int
    inputs: List[object]
    outputs: List[object]
    specific_config: Dict[str, object]

    def __init__(self, layer_config, serial_index: int):
        self.class_name = layer_config["class_name"]
        self.name = layer_config["config"]["name"]
        self.serial_index = serial_index
        self.specific_config = layer_config["config"]

        if serial_index is not None:
            self.inputs = [serial_index - 1]
        else:
            # 'inbound_nodes': [[['conv2d_2', 0, 0, {}], ['conv2d_3', 0, 0, {}]]]
            if len(layer_config["inbound_nodes"]) > 0:
                self.inputs = [(t[0], t[1], t[2]) for t in layer_config["inbound_nodes"][0]]
            else:
                self.inputs = []

    def get_output_key(self, index: int) -> object:
        assert index == 0  # layer with multiple output is currently not supported
        if self.serial_index is None:
            return self.name, 0, 0
        else:
            return self.serial_index


class KerasConverter(Converter[KerasOperator]):
    _weight_dataset: h5py.Group

    def convert_core(self, model: h5py.File, input_shapes: List[List[int]]) -> Graph:
        model_config = json.loads(model.attrs["model_config"])
        self._weight_dataset = model["model_weights"]
        if model_config["class_name"] == "Sequential":
            return self.convert_core_sequential(model_config, input_shapes)
        elif model_config["class_name"] == "Model":
            return self.convert_core_model(model_config, input_shapes)
        else:
            raise NotImplementedError("Unknown model type")

    def serialize_operator_type(self, operator: KerasOperator) -> str:
        return operator.class_name

    def convert_core_sequential(self, model_config: Dict[str, object], input_shapes: List[List[int]]) -> Graph:
        # set input variables
        assert len(input_shapes) == 1
        graph_inputs = []
        for input_shape in input_shapes:
            order = None
            if len(input_shape) == 1:
                order = OrderC
            elif len(input_shape) == 2:
                order = OrderNC
            elif len(input_shape) == 4:
                # Assuming data_format == "channels_last":
                order = OrderNHWC
            else:
                raise NotImplementedError("Input shape must be 1,2,4 dimensions")
            v = Variable(input_shape, order)
            self.set_variable(-1, v)
            graph_inputs.append(v)

        # generate operator objects
        for serial_index, layer_config in enumerate(model_config["config"]):
            operator = KerasOperator(layer_config, serial_index)
            self.convert_operator(operator)

        # output of whole graph = output of final layer
        graph_outputs = [self.get_variable(len(model_config["config"]) - 1)]

        return Graph(graph_inputs, graph_outputs)

    def convert_core_model(self, model_config: Dict[str, object], input_shapes: List[List[int]]) -> Graph:
        self._preprocess_zeropadding2d(model_config)

        input_layers = model_config["config"]["input_layers"]  # [['input_1', 0, 0]]
        assert len(input_layers) == len(input_shapes)
        graph_inputs = []
        for input_layer, input_shape in zip(input_layers, input_shapes):
            order = None
            if len(input_shape) == 1:
                order = OrderC
            elif len(input_shape) == 2:
                order = OrderNC
            elif len(input_shape) == 4:
                # Assuming data_format == "channels_last":
                order = OrderNHWC
            else:
                raise NotImplementedError("Input shape must be 1,2,4 dimensions")
            v = Variable(input_shape, order)

            graph_inputs.append(v)
            self.set_variable(tuple(input_layer), v)  # key: ('input_1', 0, 0)

        for layer_config in model_config["config"]["layers"]:
            layer = KerasOperator(layer_config, None)
            self.convert_operator(layer)

        output_layers = model_config["config"]["output_layers"]
        graph_outputs = []
        for output_layer in output_layers:
            graph_outputs.append(self.get_variable(tuple(output_layer)))

        return Graph(graph_inputs, graph_outputs)

    def create_constant_array(self, operator: KerasOperator, key: str) -> np.ndarray:
        return self._weight_dataset[f"{operator.name}/{operator.name}/{key}"].value

    def create_constant_variable(self, operator: KerasOperator, key: str, order: Order) -> ConstantVariable:
        return ConstantVariable(self.create_constant_array(operator, key), order)

    def _preprocess_zeropadding2d(self, model_config):
        """
        ZeroPadding2D -> Conv2D のパターンについて、Conv2Dのpaddingに統合してZeroPadding2D layerを消去する
        :return:
        """

        zeropad_layers = dict()  # レイヤーの出力変数名とレイヤー情報
        for layer in model_config["config"]["layers"]:
            layer_class_name = layer["class_name"]
            if layer_class_name == "ZeroPadding2D":
                output_key = (layer["name"], 0, 0)
                zeropad_layers[output_key] = layer
            elif layer_class_name == "Conv2D":
                # 自身の入力がZeroPaddingの入力ならば対応する
                input_key = tuple(layer["inbound_nodes"][0][0][:3])
                if input_key in zeropad_layers:
                    pre_zeropad_layer = zeropad_layers[input_key]
                    padding_raw = pre_zeropad_layer["config"]["padding"]  # [[top, bottom], [left, right]]
                    assert padding_raw[0][0] == padding_raw[0][1]
                    assert padding_raw[1][0] == padding_raw[1][1]
                    assert layer["config"]["padding"] == "valid"
                    # Conv2Dのpaddingのところに代入し、Conv2Dレイヤーの変換時に利用
                    layer["config"]["padding"] = (padding_raw[0][0], padding_raw[1][0])
                    # zeropadding layerの入力をconv自体の入力に置き換える
                    layer["inbound_nodes"] = pre_zeropad_layer["inbound_nodes"]

        for layer in zeropad_layers.values():
            model_config["config"]["layers"].remove(layer)


@KerasConverter.register_handler("InputLayer")
def _convert_input_layer(converter: KerasConverter, operator: KerasOperator):
    """
    Dummy layer
    Args:
        converter:
        operator:

    Returns:

    """
    pass


@KerasConverter.register_handler("Dense")
def _convert_dense(converter: KerasConverter, operator: KerasOperator):
    assert len(operator.inputs) == 1
    x = converter.get_variable(operator.inputs[0])
    w = converter.create_constant_variable(operator, "kernel:0", OrderCN)
    linear_opr = Linear(None)

    y, = linear_opr(x, w)

    if operator.specific_config["use_bias"]:
        bias = converter.create_constant_variable(operator, "bias:0", OrderC)
        bias_opr = AxiswiseBias(None, Axis.C)
        y, = bias_opr(y, bias)

    act_opr: Operator = None
    activation_type: str = operator.specific_config["activation"]
    if activation_type == "relu":
        act_opr = Relu(None)
    elif activation_type == "softmax":
        warn("omitting softmax activation")
    elif activation_type == "linear":
        pass
    else:
        raise NotImplementedError(f"Unknown activation {activation_type}")

    if act_opr is not None:
        y, = act_opr(y)

    converter.set_variable(operator.get_output_key(0), y)


@KerasConverter.register_handler("Dropout")
def _convert_dropout(converter: KerasConverter, operator: KerasOperator):
    x = converter.get_variable(operator.inputs[0])
    warn("omitting dropout")

    converter.set_variable(operator.get_output_key(0), x)


@KerasConverter.register_handler("Conv2D")
def _convert_conv2d(converter: KerasConverter, operator: KerasOperator):
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
    x = converter.get_variable(operator.inputs[0])
    assert operator.specific_config["data_format"] == "channels_last"
    w = converter.create_constant_variable(operator, "kernel:0", OrderHWCN)  # order does not depend on data_format
    ksize: Tuple[int, int] = tuple(operator.specific_config["kernel_size"])
    stride: Tuple[int, int] = tuple(operator.specific_config["strides"])
    padding_keras: str = operator.specific_config["padding"]  # valid or same
    if isinstance(padding_keras, tuple):
        # preprocess_zeropadding2d
        padding = padding_keras
    elif padding_keras == "valid":
        padding = (0, 0)
    elif padding_keras == "same":
        padding = (ksize[0] // 2, ksize[1] // 2)
    else:
        raise ValueError("Unknown padding")

    conv2d_opr = Convolution2D(None,
                               ksize=ksize,
                               stride=stride,
                               padding=padding)
    y, = conv2d_opr(x, w)

    if operator.specific_config["use_bias"]:
        bias = converter.create_constant_variable(operator, "bias:0", OrderC)
        bias_opr = AxiswiseBias(None, Axis.C)
        y, = bias_opr(y, bias)

    act_opr: Operator = None
    activation_type: str = operator.specific_config["activation"]
    if activation_type == "relu":
        act_opr = Relu(None)
    elif activation_type == "softmax":
        warn("omitting softmax activation")
    elif activation_type == "linear":
        pass
    else:
        raise NotImplementedError(f"Unknown activation {activation_type}")

    if act_opr is not None:
        y, = act_opr(y)

    converter.set_variable(operator.get_output_key(0), y)


@KerasConverter.register_handler("MaxPooling2D")
def _convert_max_pooling2d(converter: KerasConverter, operator: KerasOperator):
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
    x = converter.get_variable(operator.inputs[0])
    ksize: Tuple[int, int] = tuple(operator.specific_config["pool_size"])
    stride: Tuple[int, int] = tuple(operator.specific_config["strides"])
    padding_keras: str = operator.specific_config["padding"]  # valid or same
    if isinstance(padding_keras, tuple):
        # preprocess_zeropadding2d
        padding = padding_keras
    elif padding_keras == "valid":
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

    converter.set_variable(operator.get_output_key(0), y)


@KerasConverter.register_handler("AveragePooling2D")
def convert_layer_average_pooling2d(converter: KerasConverter, operator: KerasOperator):
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
    x = converter.get_variable(operator.inputs[0])
    ksize: Tuple[int, int] = tuple(operator.specific_config["pool_size"])
    stride: Tuple[int, int] = tuple(operator.specific_config["strides"])
    padding_keras: str = operator.specific_config["padding"]  # valid or same
    if isinstance(padding_keras, tuple):
        # preprocess_zeropadding2d
        padding = padding_keras
    elif padding_keras == "valid":
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

    converter.set_variable(operator.get_output_key(0), y)


@KerasConverter.register_handler("GlobalAveragePooling2D")
def convert_layer_global_average_pooling2d(converter: KerasConverter, operator: KerasOperator):
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
    x = converter.get_variable(operator.inputs[0])

    ksize: Tuple[int, int] = (x.shape_dict[Axis.H], x.shape_dict[Axis.W])
    average_pooling_2d_opr = AveragePooling2D(None,
                                              ksize=ksize,
                                              stride=(1, 1),
                                              padding=(0, 0))
    y, = average_pooling_2d_opr(x)

    # flatten without changing memory layout
    in_axes = y.order.axes.copy()
    assert in_axes[0] == Axis.N
    in_axes.remove(Axis.N)

    flatten_opr = Flatten(None, in_axes=in_axes, out_axis=Axis.C)
    y, = flatten_opr(y)

    converter.set_variable(operator.get_output_key(0), y)


@KerasConverter.register_handler("Flatten")
def _convert_flatten(converter: KerasConverter, operator: KerasOperator):
    """
    Example:
      {'class_name': 'Flatten',
'config': {'name': 'flatten_1', 'trainable': True}},

    :param layer_config:
    :param inputs:
    :return:
    """
    assert len(operator.inputs) == 1
    x = converter.get_variable(operator.inputs[0])
    in_axes = x.order.axes.copy()
    assert in_axes[0] == Axis.N
    in_axes.remove(Axis.N)
    flatten_opr = Flatten(None, in_axes=in_axes, out_axis=Axis.C)
    y, = flatten_opr(x)

    converter.set_variable(operator.get_output_key(0), y)


@KerasConverter.register_handler("Concatenate")
def _convert_concatenate(converter: KerasConverter, operator: KerasOperator):
    """
    Example:
      {'name': 'mixed0', 'trainable': True, 'axis': 3}

    :param layer_config:
    :param inputs:
    :return:
    """
    xs = [converter.get_variable(input_key) for input_key in operator.inputs]
    axis = xs[0].order.axes[operator.specific_config["axis"]]
    concat_opr = Concat(None, axis=axis)
    y, = concat_opr(*xs)

    converter.set_variable(operator.get_output_key(0), y)


@KerasConverter.register_handler("Add")
def _convert_add(converter: KerasConverter, operator: KerasOperator):
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
    xs = [converter.get_variable(input_key) for input_key in operator.inputs]
    sum_opr = ElementwiseSum(None)
    y, = sum_opr(*xs)

    converter.set_variable(operator.get_output_key(0), y)


@KerasConverter.register_handler("Activation")
def _convert_activation(converter: KerasConverter, operator: KerasOperator):
    assert len(operator.inputs) == 1
    y = converter.get_variable(operator.inputs[0])

    act_opr: Operator = None
    activation_type: str = operator.specific_config["activation"]
    if activation_type == "relu":
        act_opr = Relu(None)
    elif activation_type == "softmax":
        warn("omitting softmax activation")
    elif activation_type == "linear":
        pass
    else:
        raise NotImplementedError(f"Unknown activation {activation_type}")

    if act_opr is not None:
        y, = act_opr(y)

    converter.set_variable(operator.get_output_key(0), y)


@KerasConverter.register_handler("BatchNormalization")
def _convert_batch_normalization(converter: KerasConverter, operator: KerasOperator):
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
    x = converter.get_variable(operator.inputs[0])

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

    converter.set_variable(operator.get_output_key(0), y)
