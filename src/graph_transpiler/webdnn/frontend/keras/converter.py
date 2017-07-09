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
import tensorflow as tf

from webdnn.frontend.converter import Converter
from webdnn.graph.graph import Graph
from webdnn.graph.order import OrderNC, Order, OrderNHWC, OrderNTC
from webdnn.graph.placeholder import Placeholder
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable

if not "2." <= keras.__version__ < "3.":
    raise ValueError(f"WebDNN supports Keras v2.*.*. Currently, keras {keras.__version__} is installed.")


def get_default_order(tf_tensor: tf.Tensor):
    if len(tf_tensor.shape) == 2:
        return OrderNC

    elif len(tf_tensor.shape) == 3:
        return OrderNTC

    elif len(tf_tensor.shape) == 4:
        return OrderNHWC

    else:
        raise NotImplementedError(f"Unknown default data order: {tf_tensor}")


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

    def convert(self, model: keras.models.Model, input_orders: List[Order] = None) -> Graph:
        """
        Convert kerasmodel into WebDNN IR Graph. Currently, only TensorFlow backend is supported.

        Args:
            model (`keras.models.Model`): keras model
            input_orders (list of `webdnn.graph.order.Order`): order of input tensors. If `None` is passed, default order
                (`OrderNC` for 2D, `OrderNTC` for 3D, `OrderNHWC` for 4D) is used. If `input_orders=None`, default orders
                are assigned to all input tensors. If `input_orders[0]=None`, only first input tensor are converted with
                the default order.

        Returns:
            (:class:`~webdnn.graph.graph.Graph`): WebDNN IR Graph
        """
        if not model.built:
            model.build(None)

        self._convert_tensors(model.inputs, input_orders)

        for depth in sorted(list(model.nodes_by_depth.keys()), reverse=True):
            for node in model.nodes_by_depth[depth]:
                self.convert_operator(node.outbound_layer)

                # Check that all output tensors from current layer are converted into WebDNN Variable
                for tensor in node.output_tensors:
                    if not self.has_variable(tensor):
                        raise AssertionError(
                            f"[KerasConverter] {node.outbound_layer} outputs {tensor}, but it was not converted into "
                            f"WebDNN Variable by {self._handler_map[self.__class__.__name__][self.serialize_operator_type(node.outbound_layer)]}")

        return Graph([self.get_variable(t) for t in _to_list(self.get_input_tensor(model))],
                     [self.get_variable(t) for t in _to_list(self.get_output_tensor(model))])

    def _convert_tensors(self, tf_tensors: List[tf.Tensor], orders: List[Order]):
        if orders is None:
            orders = [None for _ in tf_tensors]

        orders = [get_default_order(tf_tensor) if order is None else order
                  for tf_tensor, order in zip(tf_tensors, orders)]

        assert len(tf_tensors) == len(orders), f"[KerasConverter] Number of specified orders is mismatched for number " \
                                               f"of tensors: tensors={tf_tensors} orders={orders}"

        variables = []
        for tf_tensor, order in zip(tf_tensors, orders):
            shape = [self._placeholder_N if d.value is None else d.value for d in tf_tensor.shape]
            variable = Variable(shape, order)
            self.set_variable(tf_tensor, variable)
            variables.append(variable)

        return variables

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

        KerasConverter has counters about how many times this method is called for each keras operator. At first time,
        this method returns the first input tensors (= `k_op.get_input_at(0)`) and increments the counter. When call
        this method again, the second input tensors (= `k_op.get_input_at(1)`) is returned. Therefore, you should call
        this method just once in your converter handler.

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

        KerasConverter has counters about how many times this method is called for each keras operator. At first time,
        this method returns the first output tensors (= `k_op.get_output_at(0)`) and increments the counter. When call
        this method again, the second output tensors (= `k_op.get_output_at(1)`) is returned. Therefore, you should call
        this method just once in your converter handler.

        *This method is provided only for implementing custom converter handler.*

        Args:
            k_op (keras.layers.Layer): keras operator

        Returns:
            (list of tensorflow.Tensor): list of output tensor(s). Even if only one element, it's wrapped in a list.
        """
        index = self._output_index_dict[k_op]
        self._output_index_dict[k_op] += 1
        return _to_list(k_op.get_output_at(index))
