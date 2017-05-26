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
from webdnn.graph.operators.average_pooling_2d import AveragePooling2D
from webdnn.graph.operators.axiswise_bias import AxiswiseBias
from webdnn.graph.operators.axiswise_scale import AxiswiseScale
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


class CommonGraphConverter:
    model_config: Dict[str, object]
    weights: h5py.Group

    def __init__(self, model_config: Dict[str, object], weights: h5py.Group):
        self.model_config = model_config
        self.weights = weights

    def convert(self, input_shapes: List[List[int]]) -> Graph:
        pass

    def convert_layer(self, layer_class_name: str, layer_config: Dict[str, object], inputs: List[Variable]) -> List[
        Variable]:
        outputs = None
        if layer_class_name == "Dense":
            outputs = self.convert_layer_dense(layer_config, inputs)
        elif layer_class_name == "Conv2D":
            outputs = self.convert_layer_conv2d(layer_config, inputs)
        elif layer_class_name == "MaxPooling2D":
            outputs = self.convert_layer_maxpooling2d(layer_config, inputs)
        elif layer_class_name == "GlobalAveragePooling2D":
            outputs = self.convert_layer_globalaveragepooling2d(layer_config, inputs)
        elif layer_class_name == "Flatten":
            outputs = self.convert_layer_flatten(layer_config, inputs)
        elif layer_class_name == "Add":
            outputs = self.convert_layer_add(layer_config, inputs)
        elif layer_class_name == "Dropout":
            warn("Omitting Dropout layer")
            outputs = inputs
        else:
            raise NotImplementedError(f"Unknown Layer {layer_class_name}")
        return outputs

    def convert_layer_dense(self, layer_config: Dict[str, object], inputs: List[Variable]) -> List[Variable]:
        assert len(inputs) == 1
        input = inputs[0]
        name: str = layer_config["name"]
        weight_array = self.weights[f"{name}/{name}/kernel:0"].value
        weight_var = ConstantVariable(weight_array, OrderCN)  # shape: (in, out)
        linear_opr = Linear(name)
        y, = linear_opr(input, weight_var)

        if layer_config["use_bias"]:
            bias_array = self.weights[f"{name}/{name}/bias:0"].value
            bias_var = ConstantVariable(bias_array, OrderC)
            bias_opr = AxiswiseBias(name + "_bias", Axis.C)
            y, = bias_opr(y, bias_var)

        act_opr: Operator = None
        activation_type: str = layer_config["activation"]
        if activation_type == "relu":
            act_opr = Relu(name + "_activation")
        elif activation_type == "softmax":
            warn("omitting softmax activation")
        else:
            raise NotImplementedError(f"Unknown activation {activation_type}")

        if act_opr is not None:
            y, = act_opr(y)

        return [y]

    def convert_layer_conv2d(self, layer_config: Dict[str, object], inputs: List[Variable]) -> List[Variable]:
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
        assert len(inputs) == 1
        input = inputs[0]
        name: str = layer_config["name"]
        weight_array = self.weights[f"{name}/{name}/kernel:0"].value
        assert layer_config["data_format"] == "channels_last"
        weight_var = ConstantVariable(weight_array, OrderHWCN)  # order does not depend on data_format
        ksize: Tuple[int, int] = tuple(layer_config["kernel_size"])
        stride: Tuple[int, int] = tuple(layer_config["strides"])
        padding_keras: str = layer_config["padding"]  # valid or same
        if padding_keras == "valid":
            padding = (0, 0)
        elif padding_keras == "same":
            padding = (ksize[0] // 2, ksize[1] // 2)
        else:
            raise ValueError("Unknown padding")

        conv2d_opr = Convolution2D(name,
                                   ksize=ksize,
                                   stride=stride,
                                   padding=padding)
        y, = conv2d_opr(input, weight_var)

        if layer_config["use_bias"]:
            bias_array = self.weights[f"{name}/{name}/bias:0"].value
            bias_var = ConstantVariable(bias_array, OrderC)
            bias_opr = AxiswiseBias(name + "_bias", Axis.C)
            y, = bias_opr(y, bias_var)

        act_opr: Operator = None
        activation_type: str = layer_config["activation"]
        if activation_type == "relu":
            act_opr = Relu(name + "_activation")
        elif activation_type == "softmax":
            warn("omitting softmax activation")
        else:
            raise NotImplementedError(f"Unknown activation {activation_type}")

        if act_opr is not None:
            y, = act_opr(y)

        return [y]

    def convert_layer_maxpooling2d(self, layer_config: Dict[str, object], inputs: List[Variable]) -> List[Variable]:
        """
        Example:
          {'class_name': 'MaxPooling2D',
   'config': {'data_format': 'channels_last',
    'name': 'max_pooling2d_1',
    'padding': 'valid',
    'pool_size': [2, 2],
    'strides': [2, 2],
    'trainable': True}},

        :param layer_config: 
        :param inputs: 
        :return: 
        """
        assert len(inputs) == 1
        input = inputs[0]
        name: str = layer_config["name"]
        ksize: Tuple[int, int] = tuple(layer_config["pool_size"])
        stride: Tuple[int, int] = tuple(layer_config["strides"])
        padding_keras: str = layer_config["padding"]  # valid or same
        if padding_keras == "valid":
            padding = (0, 0)
        elif padding_keras == "same":
            padding = (ksize[0] // 2, ksize[1] // 2)
        else:
            raise ValueError("Unknown padding")

        max_pooling_2d_opr = MaxPooling2D(name,
                                          ksize=ksize,
                                          stride=stride,
                                          padding=padding)
        y, = max_pooling_2d_opr(input)

        return [y]

    def convert_layer_globalaveragepooling2d(self, layer_config: Dict[str, object], inputs: List[Variable]) -> List[
        Variable]:
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
        assert len(inputs) == 1
        input = inputs[0]
        name: str = layer_config["name"]
        ksize: Tuple[int, int] = (input.shape_dict[Axis.H], input.shape_dict[Axis.W])

        average_pooling_2d_opr = AveragePooling2D(name,
                                                  ksize=ksize,
                                                  stride=(1, 1),
                                                  padding=(0, 0))
        y, = average_pooling_2d_opr(input)

        # データ順序を変えずに2Dにする
        in_axes = y.order.axes.copy()
        assert in_axes[0] == Axis.N
        in_axes.remove(Axis.N)
        flatten_opr = Flatten(name + "_flatten", in_axes=in_axes, out_axis=Axis.C)
        y, = flatten_opr(y)

        return [y]

    def convert_layer_flatten(self, layer_config: Dict[str, object], inputs: List[Variable]) -> List[Variable]:
        """
        Example:
          {'class_name': 'Flatten',
   'config': {'name': 'flatten_1', 'trainable': True}},

        :param layer_config: 
        :param inputs: 
        :return: 
        """
        assert len(inputs) == 1
        input = inputs[0]
        name: str = layer_config["name"]

        # データ順序を変えずに2Dにするだけ
        in_axes = input.order.axes.copy()
        assert in_axes[0] == Axis.N
        in_axes.remove(Axis.N)
        flatten_opr = Flatten(name, in_axes=in_axes, out_axis=Axis.C)
        y, = flatten_opr(input)

        return [y]

    def convert_layer_add(self, layer_config: Dict[str, object], inputs: List[Variable]) -> List[Variable]:
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
        name: str = layer_config["name"]

        sum_opr = ElementwiseSum(name)
        y, = sum_opr(*inputs)

        return [y]


class SequentialGraphConverter(CommonGraphConverter):
    def __init__(self, model_config: Dict[str, object], weights: h5py.Group):
        super().__init__(model_config, weights)

    def convert(self, input_shapes: List[List[int]]) -> Graph:
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
            graph_inputs.append(v)

        current_vars = graph_inputs
        for layer in self.model_config["config"]:
            current_vars = self.convert_layer(layer["class_name"], layer["config"], current_vars)
        graph_outputs = current_vars

        return Graph(graph_inputs, graph_outputs)


class ModelGraphConverter(CommonGraphConverter):
    def __init__(self, model_config: Dict[str, object], weights: h5py.Group):
        super().__init__(model_config, weights)

    def convert(self, input_shapes: List[List[int]]) -> Graph:
        input_layers = self.model_config["config"]["input_layers"]  # [['input_1', 0, 0]]
        # Variableは(layer_name, 0, 0)という形式のキーで管理
        var_dict = {}

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
            var_dict[tuple(input_layer)] = v  # key: ('input_1', 0, 0)

        for layer in self.model_config["config"]["layers"]:
            layer_class_name = layer["class_name"]
            if layer_class_name == "InputLayer":
                # 入力を表すダミーレイヤー
                continue
            # 入力変数をリストにまとめる
            input_variables = []
            assert len(layer["inbound_nodes"]) == 1  # [[var1, var2, ...]]
            for inbound_node in layer["inbound_nodes"][0]:
                key = (inbound_node[0], inbound_node[1], inbound_node[2])
                assert inbound_node[3] == {}
                input_variables.append(var_dict[key])

            output_variables = self.convert_layer(layer_class_name, layer["config"], input_variables)
            assert len(output_variables) == 1  # 複数出力の時の表現を認識できない
            key = (layer["name"], 0, 0)
            assert key not in var_dict
            var_dict[key] = output_variables[0]

        output_layers = self.model_config["config"]["output_layers"]
        graph_outputs = []
        for output_layer in output_layers:
            graph_outputs.append(var_dict[tuple(output_layer)])

        return Graph(graph_inputs, graph_outputs)


class KerasGraphConverter:
    def __init__(self):
        pass

    def convert(self, model: h5py.File, input_shapes: List[List[int]]) -> Graph:
        model_config = json.loads(model.attrs["model_config"])
        if model_config["class_name"] == "Sequential":
            converter = SequentialGraphConverter(model_config, model["model_weights"])
        elif model_config["class_name"] == "Model":
            converter = ModelGraphConverter(model_config, model["model_weights"])
        else:
            raise NotImplementedError("Non-sequential model is currently not implemented")

        return converter.convert(input_shapes)
