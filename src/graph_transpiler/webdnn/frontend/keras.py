# -*- coding:utf-8 -*-

"""
Keras model -> Graph object converters
Assuming Keras 2.0.4

Currently, the system assumes the model is trained with "data_format" == "channels_last".
If this is not the case, Flatten layer which follows Convolution have to change the order of variable.
Convolution implementation is currently assuming variable is NHWC.
"""

import json
from typing import List, Tuple, Dict
from typing import Optional

import h5py
import numpy as np

from webdnn.frontend.converter import Converter
from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.operator import Operator
from webdnn.graph.operators.average_pooling_2d import AveragePooling2D
from webdnn.graph.operators.axiswise_bias import AxiswiseBias
from webdnn.graph.operators.axiswise_scale import AxiswiseScale
from webdnn.graph.operators.concat import Concat
from webdnn.graph.operators.convolution2d import Convolution2D
from webdnn.graph.operators.elementwise_sum import ElementwiseSum
from webdnn.graph.operators.embedding import Embedding
from webdnn.graph.operators.flatten import Flatten
from webdnn.graph.operators.linear import Linear
from webdnn.graph.operators.lstm import LSTM
from webdnn.graph.operators.max_pooling_2d import MaxPooling2D
from webdnn.graph.operators.relu import Relu
from webdnn.graph.operators.sigmoid import Sigmoid
from webdnn.graph.operators.zero_padding_2d import ZeroPadding2D
from webdnn.graph.order import OrderNC, OrderC, OrderCN, OrderHWCN, \
    OrderNHWC, Order
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable
from webdnn.util import console


class KerasInput:
    inbound_layer_name: str
    node_index: int
    tensor_index: int
    kwargs: Dict
    key: Tuple[str, int, int]

    def __init__(self, inbound_layer_name: str, node_index: int, tensor_index: int, kwargs: Optional[Dict] = None):
        self.inbound_layer_name = inbound_layer_name
        self.node_index = node_index
        self.tensor_index = tensor_index
        self.kwargs = kwargs or {}
        self.key = (inbound_layer_name, node_index, tensor_index)


class KerasOperator:
    class_name: str
    name: str
    inputs: List[Variable]
    inputs_kwargs: List[Dict[str, object]]
    outputs: List[Variable]
    specific_config: Dict[str, object]

    def __init__(self, layer_config, inputs: List[Variable], inputs_kwargs: List[Dict[str, object]]):
        self.class_name = layer_config["class_name"]
        self.name = layer_config["config"]["name"]
        self.specific_config = layer_config["config"]
        self.inputs = inputs
        self.inputs_kwargs = inputs_kwargs
        self.outputs = None


class KerasConverter(Converter[KerasOperator]):
    _weight_dataset: h5py.Group
    _global_input_variables: List[Variable]
    _global_output_variables: List[Variable]
    _variable_table_stack = List[Dict[object, Variable]]
    _container_name_stack = List[str]
    _constant_variables: Dict[str, ConstantVariable]

    def convert_core(self, model: h5py.File, input_shapes: List[List[int]]) -> Graph:
        model_config = json.loads(model.attrs["model_config"])

        self._variable_table_stack = []
        self._container_name_stack = []
        self._constant_variables = {}
        self._global_input_variables = []
        for input_shape in input_shapes:
            order = None
            if len(input_shape) == 1:
                order = OrderC
            elif len(input_shape) == 2:
                order = OrderNC  # fixme for LSTM
            elif len(input_shape) == 4:
                # Assuming data_format == "channels_last":
                order = OrderNHWC
            else:
                raise NotImplementedError("Input shape must be 1,2,4 dimensions")
            v = Variable(input_shape, order)
            self._global_input_variables.append(v)
        self._weight_dataset = model["model_weights"]
        if model_config["class_name"] == "Sequential":
            self.convert_core_sequential(model_config)
        elif model_config["class_name"] == "Model":
            self.convert_core_model(model_config)
        else:
            raise NotImplementedError("Unknown model type")
        return Graph(self._global_input_variables, self._global_output_variables)

    def serialize_operator_type(self, operator: KerasOperator) -> str:
        return operator.class_name

    def convert_core_sequential(self, layer_config: Dict[str, object]):
        top_level = "inbound_nodes" not in layer_config
        if top_level:
            # top-level container
            assert len(self._global_input_variables) == 1, "sequential model can take only one input variable"
            input_nodes = [[self._global_input_variables[0]]]
        else:
            self._container_name_stack.append(layer_config["name"])
            input_nodes = []
            for inbound_node in layer_config["inbound_nodes"]:
                assert len(inbound_node) == 1, "sequential model can take only one input variable"
                input_var_info = inbound_node[0]  # ['conv2d_2', 0, 0, {}]
                assert input_var_info[3] == {}, "input node to sequential model cannot have arguments"
                input_nodes.append([self.get_variable(tuple(input_var_info[:3]))])

        for i, input_node in enumerate(input_nodes):
            node_index = i + 1  # Container node_index origin from 1
            # generate operator objects
            current_var = input_node[0]
            self._variable_table_stack.append(self._variable_table[self.__class__.__name__])
            self._variable_table[self.__class__.__name__] = {}
            for serial_index, sub_layer_config in enumerate(layer_config["config"]):
                if sub_layer_config["class_name"] == "Sequential":
                    self.convert_core_sequential(sub_layer_config)
                elif sub_layer_config["class_name"] == "Model":
                    self.convert_core_model(sub_layer_config)
                else:
                    operator = KerasOperator(sub_layer_config, [current_var], [{}])
                    self.convert_operator(operator)
                    current_var = operator.outputs[0]

            self._variable_table[self.__class__.__name__] = self._variable_table_stack.pop()
            # output of whole graph = output of final layer
            if top_level:
                self._global_output_variables = [current_var]
            else:
                self.set_variable((layer_config["name"], node_index, 0), current_var)

        if not top_level:
            self._container_name_stack.pop()

    def convert_core_model(self, layer_config: Dict[str, object]):
        top_level = "inbound_nodes" not in layer_config
        if top_level:
            # top-level container
            input_nodes = [self._global_input_variables]
            self._global_output_variables = []
        else:
            self._container_name_stack.append(layer_config["name"])
            input_nodes = []
            for inbound_node in layer_config["inbound_nodes"]:
                input_node = []
                for input_var_info in inbound_node:  # ['conv2d_2', 0, 0, {}]
                    assert input_var_info[3] == {}, "input node to graph model cannot have arguments"
                    input_node.append(self.get_variable(tuple(input_var_info[:3])))
                input_nodes.append(input_node)

        for i, input_node in enumerate(input_nodes):
            node_index = i + 1  # Container node_index origin from 1
            # generate operator objects
            self._variable_table_stack.append(self._variable_table[self.__class__.__name__])
            local_variable_table = {}
            # assign inbound_node to local variable table
            for j, input_key in enumerate(layer_config["config"]["input_layers"]):  # input_key: ['input_1', 0, 0]
                # variable to this container is referred with input_key
                local_variable_table[tuple(input_key)] = input_node[j]
            self._variable_table[self.__class__.__name__] = local_variable_table
            for serial_index, sub_layer_config in enumerate(layer_config["config"]["layers"]):
                if sub_layer_config["class_name"] == "Sequential":
                    self.convert_core_sequential(sub_layer_config)
                elif sub_layer_config["class_name"] == "Model":
                    self.convert_core_model(sub_layer_config)
                else:
                    for sub_layer_node_index, sub_layer_inbound_node in enumerate(sub_layer_config["inbound_nodes"]):
                        # 'inbound_nodes': [[['input_2', 0, 0, {}]], [['conv2d_2', 0, 0, {}]]]
                        # gather input variables
                        sub_layer_inputs = []
                        sub_layer_input_kwargs = []
                        for sub_layer_input_var_info in sub_layer_inbound_node:
                            sub_layer_inputs.append(self.get_variable(tuple(sub_layer_input_var_info[:3])))
                            sub_layer_input_kwargs.append(sub_layer_input_var_info[3])

                        operator = KerasOperator(sub_layer_config, sub_layer_inputs, sub_layer_input_kwargs)
                        self.convert_operator(operator)

                        # assign outputs
                        for sub_layer_output_tensor_index, sub_layer_output_var in enumerate(operator.outputs):
                            local_variable_table[(sub_layer_config["name"], sub_layer_node_index,
                                                  sub_layer_output_tensor_index)] = sub_layer_output_var

            self._variable_table[self.__class__.__name__] = self._variable_table_stack.pop()
            # output of whole graph is desginated in layer_config["output_layers"]
            for output_tensor_index, output_layer in enumerate(layer_config["config"]["output_layers"]):
                # local ['conv2d_3', 0, 0] -> global ['model_1', 1, 0]
                if top_level:
                    self._global_output_variables.append(local_variable_table[tuple(output_layer)])
                else:
                    self.set_variable((layer_config["name"], node_index, output_tensor_index),
                                      local_variable_table[tuple(output_layer)])

        if not top_level:
            self._container_name_stack.pop()

    def _get_weight_value(self, weight_key: str) -> np.ndarray:
        try:
            weight_object = self._weight_dataset[weight_key]
        except KeyError:
            try:
                weight_key_split = weight_key.split('/')
                weight_alter_key = f"{weight_key_split[0]}/{weight_key_split[1]}_1/{weight_key_split[2]}"
                weight_object = self._weight_dataset[weight_alter_key]
            except KeyError:
                console.error(f"Weight parameter {weight_key} or {weight_alter_key} does not exist in model file.")
                raise
        return weight_object.value

    def create_constant_array(self, operator: KerasOperator, key: str) -> np.ndarray:
        # when the operator is top-level, key is "{operator.name}/{operator.name}/{key}"
        # if contained in nested container, key is "{container.name}/{operator.name}/{key}"
        weight_key = self._get_key_for_constant_variable(operator, key)
        return self._get_weight_value(weight_key)

    def _get_key_for_constant_variable(self, operator: KerasOperator, key: str) -> str:
        weight_key = f"{self._container_name_stack[-1] if len(self._container_name_stack) > 0 else operator.name}/{operator.name}/{key}"
        return weight_key

    def create_constant_variable(self, operator: KerasOperator, key: str, order: Order,
                                 force_new: bool = False) -> ConstantVariable:
        weight_key = self._get_key_for_constant_variable(operator, key)
        # force_new should be used when the contents of constant variable may be modified
        if not force_new and weight_key in self._constant_variables:
            cvar = self._constant_variables[weight_key]
            assert cvar.order == order
            return cvar

        cvar = ConstantVariable(self.create_constant_array(operator, key), order)
        self._constant_variables[weight_key] = cvar
        return cvar


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
    x = operator.inputs[0]
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
    elif activation_type == "sigmoid":
        act_opr = Sigmoid(None)
    elif activation_type == "softmax":
        console.warning("[KerasConverter] omitting softmax activation")
    elif activation_type == "linear":
        pass
    else:
        raise NotImplementedError(f"Unknown activation {activation_type}")

    if act_opr is not None:
        y, = act_opr(y)

    operator.outputs = [y]


@KerasConverter.register_handler("Dropout")
def _convert_dropout(converter: KerasConverter, operator: KerasOperator):
    x = operator.inputs[0]
    console.warning("[KerasConverter] omitting dropout")

    operator.outputs = [x]


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
    x = operator.inputs[0]
    assert operator.specific_config["data_format"] == "channels_last"
    w = converter.create_constant_variable(operator, "kernel:0", OrderHWCN)  # order does not depend on data_format
    ksize: Tuple[int, int] = tuple(operator.specific_config["kernel_size"])
    stride: Tuple[int, int] = tuple(operator.specific_config["strides"])
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
    elif activation_type == "sigmoid":
        act_opr = Sigmoid(None)
    elif activation_type == "softmax":
        console.warning("[KerasConverter] omitting softmax activation")
    elif activation_type == "linear":
        pass
    else:
        raise NotImplementedError(f"Unknown activation {activation_type}")

    if act_opr is not None:
        y, = act_opr(y)

    operator.outputs = [y]


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
    x = operator.inputs[0]

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

    operator.outputs = [y]


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
    x = operator.inputs[0]
    in_axes = x.order.axes.copy()
    assert in_axes[0] == Axis.N
    in_axes.remove(Axis.N)
    flatten_opr = Flatten(None, in_axes=in_axes, out_axis=Axis.C)
    y, = flatten_opr(x)

    operator.outputs = [y]


@KerasConverter.register_handler("Concatenate")
def _convert_concatenate(converter: KerasConverter, operator: KerasOperator):
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
    xs = operator.inputs
    sum_opr = ElementwiseSum(None)
    y, = sum_opr(*xs)

    operator.outputs = [y]


@KerasConverter.register_handler("Activation")
def _convert_activation(converter: KerasConverter, operator: KerasOperator):
    assert len(operator.inputs) == 1
    y = operator.inputs[0]

    act_opr: Operator = None
    activation_type: str = operator.specific_config["activation"]
    if activation_type == "relu":
        act_opr = Relu(None)
    elif activation_type == "sigmoid":
        act_opr = Sigmoid(None)
    elif activation_type == "softmax":
        console.warning("[KerasConverter] omitting softmax activation")
    elif activation_type == "linear":
        pass
    else:
        raise NotImplementedError(f"Unknown activation {activation_type}")

    if act_opr is not None:
        y, = act_opr(y)

    operator.outputs = [y]


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
def _convert_zero_padding2d(converter: KerasConverter, operator: KerasOperator):
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
def _convert_embedding(converter: KerasConverter, operator: KerasOperator):
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
    w = converter.create_constant_variable(operator, "embeddings:0", OrderCN)
    embedding_opr = Embedding(None)

    y, = embedding_opr(x, w)

    operator.outputs = [y]


@KerasConverter.register_handler("LSTM")
def _convert_lstm(converter: KerasConverter, operator: KerasOperator):
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
    assert operator.specific_config["use_bias"] is True
    x = operator.inputs[0]
    w_input = converter.create_constant_variable(operator, "kernel:0", OrderCN)
    w_hidden = converter.create_constant_variable(operator, "recurrent_kernel:0", OrderCN)
    b = converter.create_constant_variable(operator, "bias:0", OrderC)
    lstm_opr = LSTM(None)

    y, = lstm_opr(x, w_input, w_hidden, b)

    operator.outputs = [y]
