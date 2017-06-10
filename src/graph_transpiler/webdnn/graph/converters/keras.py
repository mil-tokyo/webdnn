# -*- coding:utf-8 -*-

"""
Keras model -> Graph object converters
Assuming Keras 2.0.4

Currently, the system assumes the model is trained with "data_format" == "channels_last".
If this is not the case, Flatten layer which follows Convolution have to change the order of variable.
Convolution implementation is currently assuming variable is NHWC.
"""

from typing import List, Tuple, Dict

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
            self.outputs = [serial_index]
        else:
            raise NotImplementedError()

    @classmethod
    def operator_matcher(cls, operator: "KerasOperator", klass: str):
        return operator.class_name == klass


class KerasConverter(Converter[KerasOperator, object]):
    _variable_table: Dict[object, Variable]
    _weight_dataset: h5py.Group

    def convert_core(self, model: h5py.File, input_shapes: List[List[int]]) -> Graph:
        # FIXME: not share operator matcher between converters
        Converter._operator_matcher = KerasOperator.operator_matcher
        model_config = json.loads(model.attrs["model_config"])
        self._weight_dataset = model["model_weights"]
        self._variable_table = {}
        if model_config["class_name"] == "Sequential":
            return self.convert_core_sequential(model_config, input_shapes)
        elif model_config["class_name"] == "Model":
            return self.convert_core_model(model_config, input_shapes)
        else:
            raise NotImplementedError("Unknown model type")

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
        raise NotImplementedError()

    def convert_variable_core(self, variable: object, order: Order = None) -> Variable:
        raise NotImplementedError()

    def get_variable(self, key: object):
        return self._variable_table[key]

    def set_variable(self, key: object, variable: Variable):
        if key in self._variable_table:
            raise ValueError(f"Variable {key} already exists")
        self._variable_table[key] = variable

    def create_constant_array(self, operator: KerasOperator, key: str) -> np.ndarray:
        return self._weight_dataset[f"{operator.name}/{operator.name}/{key}"].value

    def create_constant_variable(self, operator: KerasOperator, key: str, order: Order) -> ConstantVariable:
        return ConstantVariable(self.create_constant_array(operator, key), order)


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
    else:
        raise NotImplementedError(f"Unknown activation {activation_type}")

    if act_opr is not None:
        y, = act_opr(y)

    converter.set_variable(operator.outputs[0], y)


@KerasConverter.register_handler("Dropout")
def _convert_dropout(converter: KerasConverter, operator: KerasOperator):
    x = converter.get_variable(operator.inputs[0])
    warn("omitting dropout")

    converter.set_variable(operator.outputs[0], x)


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
    else:
        raise NotImplementedError(f"Unknown activation {activation_type}")

    if act_opr is not None:
        y, = act_opr(y)

    converter.set_variable(operator.outputs[0], y)


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

    converter.set_variable(operator.outputs[0], y)


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

    converter.set_variable(operator.outputs[0], y)
