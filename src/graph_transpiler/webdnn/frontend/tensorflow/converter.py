# -*- coding:utf-8 -*-
import traceback
from typing import List, Union, Optional, Dict, Sequence, Tuple

from webdnn.frontend.converter import Converter, CyclicGraphError
from webdnn.frontend.util import semver
from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.optimize_rule import OptimizeRuleGroup
from webdnn.graph.order import Order
from webdnn.graph.placeholder import Placeholder
from webdnn.graph.variable import Variable
from webdnn.graph.variables.attributes.input import Input
from webdnn.graph.variables.attributes.output import Output
from webdnn.graph.variables.constant_variable import ConstantVariable
from webdnn.optimizer.sub_rules.constant_folding import ConstantFolding
from webdnn.optimizer.tensorflow_frontend_optimize_rule import TensorFlowFrontendOptimizeRule
from webdnn.util import console

FLAG_TF_INSTALLED = True

try:
    import tensorflow as tf

    VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH = semver(tf.VERSION)
    if not ((VERSION_MAJOR == 1) and (2 <= VERSION_MINOR <= 4)):
        raise NotImplementedError(f"WebDNN supports TensorFlow >=v1.2.0,<=v1.4.0 Currently, TensorFlow {tf.VERSION} is installed.")


except Exception as e:
    console.warning(traceback.format_exc())


class TensorFlowConverter(Converter["tf.Operation"]):
    """TensorFlowConverter(batch_size=1)

    Converter for `TensorFlow <https://www.tensorflow.org/>`_

    Args:
        session (:code:`tf.Session`): Session. As default, `tf.get_default_session()` is used.
    """

    def __init__(self, session: "tf.Session" = None, batch_size: int = 1):
        super(TensorFlowConverter, self).__init__()

        if not FLAG_TF_INSTALLED:
            raise ImportError("[TensorFlowConverter] Failed to import Tensorflow.")

        if session is None:
            session = tf.get_default_session()

        self.session = session
        self._batch_size = Placeholder(label=Axis.N.name, value=batch_size)

    def serialize_operator_type(self, op: "tf.Operation") -> str:
        return op.type

    def convert(self, inputs: Sequence["tf.Tensor"], outputs: Sequence["tf.Tensor"],
                order_hints: Optional[Dict[Union["tf.Tensor", "tf.Variable"], Order]] = None) -> Graph:
        """convert(model, input_orders=None)

        Args:
            inputs (list of `tf.Tensor`): tensorflow input tensors
            outputs (list of `tf.Tensor`): tensorflow output tensors
            order_hints: Order annotations which helps webdnn's optimizer.

        .. admonition:: example

            Convert TensorFlow model.

            .. code::

                import tensorflow as tf
                from webdnn.frontend.tensorflow import TensorFlowConverter

                # y = x @ W + b
                x = tf.placeholder(tf.float32, [None, 784])
                W = tf.Variable(tf.zeros([784, 10]))
                b = tf.Variable(tf.zeros([10]))
                y = tf.nn.softmax(tf.matmul(x, W) + b)

                graph = TensorFlowConverter().convert([x], [y])

        Returns:
            (:class:`~webdnn.graph.graph.Graph`): WebDNN IR Graph
        """

        for tensor in inputs:
            shape = [Placeholder() if dim.value is None else dim.value for dim in tensor.shape.dims]
            if isinstance(shape[0], Placeholder):
                shape[0] = self._batch_size
            self.set_variable(tensor, Variable(shape, Order([None] * len(shape))))

        ops = _listup_operations(inputs, outputs)
        for op in ops:
            self._convert_operator(op)
            sub_graph = Graph([self.get_variable(tf_tensor) for tf_tensor in op.inputs if self.has_variable(tf_tensor)],
                              [self.get_variable(tf_tensor) for tf_tensor in op.outputs if self.has_variable(tf_tensor)])
            old_outputs = list(sub_graph.outputs)

            # Constant folding improves possibility of conversion, because many tensors are used not only for main input variable but also
            # for other parameter like indices of operation, and WebDNN doesn't support dynamic indices operation.
            OptimizeRuleGroup([ConstantFolding()], repeat=True).optimize(sub_graph)

            # After constant folding, it need to replace old variable with new constant variable
            for tf_tensor in op.outputs:
                if not self.has_variable(tf_tensor):
                    # This tensor is not converted (ignored)
                    continue

                old_v = self.get_variable(tf_tensor)
                new_v = sub_graph.outputs[old_outputs.index(old_v)]
                if old_v != new_v:
                    self.set_variable(tf_tensor, new_v, overwrite=True)

        if order_hints:
            for tensor, order in order_hints.items():
                if isinstance(tensor, tf.Variable):
                    tensor = tensor.value()

                variable = self.get_variable(tensor)
                for axis1, axis2 in zip(variable.order.axes, order.axes):
                    axis1.unify(axis2)

        # Remove redundant ReinterpretAxis operators
        graph = Graph([self.get_variable(tensor) for tensor in inputs], [self.get_variable(tensor) for tensor in outputs])
        graph, _ = TensorFlowFrontendOptimizeRule().optimize(graph)

        for v in graph.inputs:
            v.attributes.add(Input())

        for v in graph.outputs:
            v.attributes.add(Output())

        return graph

    def convert_to_constant_variable(self, tensor: "tf.Tensor", order: Optional[Order] = None) -> ConstantVariable:
        """convert_to_constant_variable(tf_var, order)

        Convert tf.Tensor into :class:`~webdnn.graph.variables.constant_variable.ConstantVariable`.

        This method also registers the mapping information between TensorFlow variable and WebDNN constant variable.
        If specified TensorFlow variable is already registered into converter, converter checks that the shape and order
        is valid

        **This method is provided only for implementing custom converter handler.**

        Args:
            tensor (:code:`tf.Tensor`): TensorFlow tensor
            order: (:class:`~webdnn.graph.order.Order`) data order. As default, default order is used.

        Returns:
            (:class:`~webdnn.graph.variables.constant_variable.ConstantVariable`): converted variable.
        """

        data, = self.session.run([tensor])

        if self.has_variable(tensor):
            variable = self.get_variable(tensor)
            assert variable.shape == tuple(data.shape), f"[TensorFlowConverter] {tensor} is already registered before, and " \
                                                        f"shape mismatch is detected: (registered shape)=" \
                                                        f"{variable.shape}, (given tensor's shape)=" \
                                                        f"{tensor.shape}"
            if order is not None:
                assert variable.order == order, f"[TensorFlowConverter] {tensor} is already registered before, and order " \
                                                f"mismatch is detected: (registered order)={variable.order}, (given " \
                                                f"order)={order}"

        else:
            if order is None:
                order = Order([None] * data.ndim)

            variable = ConstantVariable(data, order)
            self.set_variable(tensor, variable)

        return variable


T_NODE = Union[tf.Tensor, tf.Operation]


def _listup_operations(inputs: Sequence[T_NODE], outputs: Sequence[T_NODE]):
    def get_prev_nodes(node: T_NODE) -> Sequence[T_NODE]:
        if node in inputs:
            return []

        elif isinstance(node, tf.Tensor):
            return [node.op]

        else:
            return node.inputs

    result = []  # type: List[tf.Operation]
    stack = [(node, None) for node in outputs]  # type: List[Tuple[T_NODE, T_NODE]]
    dependency_count = {}  # type: Dict[T_NODE, int]

    while len(stack) > 0:
        node_from, node_to = stack.pop()

        if node_from not in dependency_count:
            stack.append((node_from, node_to))

            prev_nodes = get_prev_nodes(node_from)
            dependency_count[node_from] = 0
            for prev_node in prev_nodes:
                if dependency_count.get(prev_node, 1) > 0:
                    dependency_count[node_from] += 1
                    stack.append((prev_node, node_from))

        elif dependency_count[node_from] == 0:
            if isinstance(node_from, tf.Operation):
                result.append(node_from)

            if node_to is not None:
                dependency_count[node_to] -= 1

        else:
            console.debug("[TensorFlowConverter] Cycle is detected in computation graph")
            console.debug("cycle starting node:")
            console.debug(node_from)

            raise CyclicGraphError("[TensorFlowConverter] Cycles are detected, but TensorFlowConverter cannot convert cyclic graph")

    return result
