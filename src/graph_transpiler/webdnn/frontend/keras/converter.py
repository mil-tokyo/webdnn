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
from webdnn.graph.order import OrderNC, Order, OrderNHWC
from webdnn.graph.placeholder import Placeholder
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable


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


