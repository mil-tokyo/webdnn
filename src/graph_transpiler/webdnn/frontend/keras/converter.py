import traceback
from collections import defaultdict
from typing import List, Optional

import numpy as np

from webdnn.frontend.converter import Converter
from webdnn.frontend.tensorflow import TensorFlowConverter
from webdnn.frontend.util import semver
from webdnn.graph.graph import Graph
from webdnn.graph.order import Order
from webdnn.graph.placeholder import Placeholder
from webdnn.graph.variable import Variable
from webdnn.graph.variables.attributes.input import Input
from webdnn.graph.variables.attributes.output import Output
from webdnn.graph.variables.constant_variable import ConstantVariable
from webdnn.util import console

FLAG_KERAS_INSTALLED = False

try:
    import keras
    import keras.backend as K
    import tensorflow as tf

    VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH = semver(keras.__version__)
    if not (VERSION_MAJOR == 2 and ((VERSION_MINOR == 1 and VERSION_PATCH >= 3) or VERSION_MINOR >= 2)):
        raise NotImplementedError(f"WebDNN supports Keras v2.*.*. Currently, keras {keras.__version__} is installed.")

    FLAG_KERAS_INSTALLED = True

except Exception as e:
    console.warning(traceback.format_exc())


def _to_list(x):
    return x if isinstance(x, (list, tuple)) else [x]


class KerasConverter(Converter["keras.layers.Layer"]):
    """KerasConverter(batch_size=1)

    Converter for `Keras <https://keras.io/>`_.

    **Limitations**

    - Only Keras v2+ is supported.
    - Only tensorflow backend is supported.
    - Only :code:`data_format="channel_last"` is supported.

    If you want to implement custom handler for your custom Keras Layer, please see :doc:`/tutorial/custom_operator/index`.

    Args:
        batch_size(int or None): input batch size. As default, keras handle the batch size as place holder (undetermined) value. If
          :code:`None` is passed, converter handles the batch size as placeholder named "N".
        use_tensorflow_converter(bool): If `True`, KerasConverter first tries to convert model by TensorFlowConverter. Then if it failed,
          retry conversion with KerasConverter itself.
    """

    def __init__(self, batch_size: int = 1, use_tensorflow_converter: bool = True):
        super(KerasConverter, self).__init__()

        if not FLAG_KERAS_INSTALLED:
            raise ImportError("[KerasConverter] Failed to import Keras.")

        if K.backend() != "tensorflow":
            raise NotImplementedError("Only TensorFlow backend is supported.")

        K.set_learning_phase(0)

        self._input_index_dict = defaultdict(lambda: 0)
        self._output_index_dict = defaultdict(lambda: 0)
        self._input_tensor_cache = None  # type: List[tf.Tensor]
        self._output_tensor_cache = None  # type: List[tf.Tensor]
        self._batch_size = batch_size
        self._use_tensorflow_converter = use_tensorflow_converter

    def convert(self, model: "keras.models.Model") -> Graph:
        """convert(model, input_orders=None)

        Convert kerasmodel into WebDNN IR Graph. First, WebDNN try to convert backend TensorFlow graph by TensorFlowConverter.
        If TensorFlowConverter failed to convert, then KerasConverter converts model by itself

        Args:
            model (`keras.models.Model`): keras model

        .. admonition:: example

            Convert pre-trained keras ResNet model.

            .. code::

                import keras
                from webdnn.frontend.keras import KerasConverter

                model = keras.applications.resnet50.ResNet50(include_top=True, weights='imagenet')
                graph = KerasConverter(batch_size=1).convert(model)

        Returns:
            (:class:`~webdnn.graph.graph.Graph`): WebDNN IR Graph
        """
        if not self._use_tensorflow_converter:
            return self._convert_fallback(model)

        else:
            # noinspection PyBroadException
            try:
                return TensorFlowConverter(session=K.get_session(), batch_size=self._batch_size).convert(model.inputs, model.outputs)

            except Exception:
                self._use_tensorflow_converter = False
                console.debug(traceback.format_exc())
                console.debug("[KerasConverter] TensorflowConverter failed to convert.")

        return self._convert_fallback(model)

    def _convert_fallback(self, model: "keras.models.Model") -> Graph:
        if not model.built:
            model.build(None)

        self._convert_tensors(model.inputs)
        for tensor in model.inputs:
            v = self.get_variable(tensor)
            if not Placeholder.check_resolved(v.shape[0]):
                v.shape[0].value = self._batch_size

        for depth in sorted(list(model._nodes_by_depth.keys()), reverse=True):
            for node in model._nodes_by_depth[depth]:
                self._convert_operator(node.outbound_layer)

                # Check that all output tensors from current layer are converted into WebDNN Variable
                for tensor in node.output_tensors:
                    if not self.has_variable(tensor):
                        raise AssertionError(
                            f"[KerasConverter] {node.outbound_layer} outputs {tensor}, but it was not converted into WebDNN Variable by "
                            f"{self._handler_map[self.__class__.__name__][self.serialize_operator_type(node.outbound_layer)]}")

        self._input_index_dict[model] -= 1
        self._output_index_dict[model] -= 1
        self._input_tensor_cache = None
        self._output_tensor_cache = None

        graph = Graph([self.get_variable(t) for t in self.get_input_tensor(model)],
                      [self.get_variable(t) for t in self.get_output_tensor(model)])

        self._input_tensor_cache = None
        self._output_tensor_cache = None

        for v in graph.inputs:
            v.attributes.add(Input())

        for v in graph.outputs:
            v.attributes.add(Output())

        return graph

    def _convert_operator(self, k_op: "keras.layers.Layer"):
        self._input_tensor_cache = None
        self._output_tensor_cache = None
        self.get_input_tensor(k_op)
        self.get_output_tensor(k_op)
        return super(KerasConverter, self)._convert_operator(k_op)

    def _convert_tensors(self, tf_tensors: List["tf.Tensor"]):
        orders = [Order([None] * tf_tensor.shape.ndims) for tf_tensor in tf_tensors]

        assert len(tf_tensors) == len(orders), f"[KerasConverter] Number of specified orders is mismatched for number " \
                                               f"of tensors: tensors={tf_tensors} orders={orders}"

        variables = []
        for tf_tensor, order in zip(tf_tensors, orders):
            shape = []
            for s, axis in zip(tf_tensor.shape, order.axes):
                shape.append(Placeholder() if s.value is None else s.value)

            variable = Variable(shape, order)
            self.set_variable(tf_tensor, variable)
            variables.append(variable)

        return variables

    def convert_to_constant_variable(self, tf_var: "tf.Variable", order: Optional[Order] = None) -> ConstantVariable:
        """convert_to_constant_variable(tf_var, order)

        Convert TensorFlow variable (parameter of kerasmodel) into
        :class:`~webdnn.graph.variables.constant_variable.ConstantVariable`.

        This method also registers the mapping information between TensorFlow variable and WebDNN constant variable.
        If specified TensorFlow variable is already registered into converter, converter checks that the shape and order
        is valid

        **This method is provided only for implementing custom converter handler.**

        Args:
            tf_var (tensorflow.Variable): TensorFlow variable
            order: (:class:`~webdnn.graph.order.Order`) data order

        Returns:
            (:class:`~webdnn.graph.variables.constant_variable.ConstantVariable`): converted variable.
        """
        data = K.batch_get_value([tf_var])[0]  # type:np.array

        if self.has_variable(tf_var):
            variable = self.get_variable(tf_var)
            assert variable.shape == tuple(data.shape), f"[KerasConverter] {tf_var} is already registered before, and " \
                                                        f"shape mismatch is detected: (registered shape)=" \
                                                        f"{variable.shape}, (given tensorflow variable's shape)=" \
                                                        f"{data.shape}"
            if order is not None:
                assert variable.order == order, f"[KerasConverter] {tf_var} is already registered before, and order " \
                                                f"mismatch is detected: (registered order)={variable.order}, (given " \
                                                f"tensorflow variable's order)={order}"

        else:
            if order is None:
                order = Order([None] * data.ndim)
            variable = ConstantVariable(data, order)
            self.set_variable(tf_var, variable)

        return variable

    def get_input_tensor(self, k_op: "keras.layers.Layer") -> List["tf.Tensor"]:
        """get_input_tensor(k_op)

        Return input tensor(s) of specified keras layer.

        **This method is provided only for implementing custom converter handler.**

        Args:
            k_op (keras.layers.Layer): keras operator

        Returns:
            (list of tensorflow.Tensor): list of input tensor(s). Even if only one element, it's wrapped in a list.
        """
        if self._input_tensor_cache:
            return self._input_tensor_cache

        index = self._input_index_dict[k_op]
        self._input_index_dict[k_op] += 1
        self._input_tensor_cache = _to_list(k_op.get_input_at(index))
        return self._input_tensor_cache

    def get_output_tensor(self, k_op: "keras.layers.Layer") -> List["tf.Tensor"]:
        """get_output_tensor(k_op)

        Return output tensor(s) of specified keras layer.

        **This method is provided only for implementing custom converter handler.**

        Args:
            k_op (keras.layers.Layer): keras operator

        Returns:
            (list of tensorflow.Tensor): list of output tensor(s). Even if only one element, it's wrapped in a list.
        """
        if self._output_tensor_cache:
            return self._output_tensor_cache

        index = self._output_index_dict[k_op]
        self._output_index_dict[k_op] += 1
        self._output_tensor_cache = _to_list(k_op.get_output_at(index))
        return self._output_tensor_cache
