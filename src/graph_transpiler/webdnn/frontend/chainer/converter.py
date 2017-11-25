# -*- coding:utf-8 -*-

"""
Chainer Link -> Graph object converters
Assuming Chainer 1.23-1.24 or 2.0
"""
import traceback
import warnings
from typing import List, Union, Sequence, Dict, Tuple

from chainer import Function
from webdnn.frontend.converter import Converter, CyclicGraphError
from webdnn.graph.graph import Graph
from webdnn.graph.order import Order
from webdnn.graph.variable import Variable
from webdnn.graph.variables.attributes.input import Input
from webdnn.graph.variables.attributes.output import Output
from webdnn.graph.variables.constant_variable import ConstantVariable
from webdnn.util import console

FLAG_CHAINER_INSTALLED = False

try:
    import chainer
    import chainer.computational_graph

    if "2." <= chainer.__version__ < "3.":
        chainer_v2 = True
        VariableNode = chainer.variable.VariableNode

    elif "1." <= chainer.__version__ < "2.":
        chainer_v2 = False
        VariableNode = chainer.variable.Variable

    else:
        raise NotImplementedError(f"WebDNN supports Chainer v1 and v2. Currently, Chainer {chainer.__version__} is installed.")

    FLAG_CHAINER_INSTALLED = True

except Exception as e:
    console.warning(traceback.format_exc())


def _to_variable_node(chainer_variable: Union["chainer.Variable", "VariableNode"]) -> "VariableNode":
    if chainer_v2 and not isinstance(chainer_variable, VariableNode):
        # noinspection PyUnresolvedReferences
        return chainer_variable.node
    else:
        # noinspection PyTypeChecker
        return chainer_variable


T_NODE = Union["VariableNode", "Function"]


def _listup_functions(inputs: Sequence[T_NODE], outputs: Sequence[T_NODE]):
    def get_prev_nodes(node: T_NODE) -> Sequence[T_NODE]:
        if node in inputs:
            return []

        elif isinstance(node, VariableNode):
            return [] if node.creator is None else [node.creator]

        else:
            return node.inputs

    result = []  # type: List[Function]
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
            if isinstance(node_from, Function):
                result.append(node_from)

            if node_to is not None:
                dependency_count[node_to] -= 1

        else:
            raise CyclicGraphError("[ChainerConverter] Cycles are detected, but ChainerConverter cannot convert cyclic graph")

    return result


class ChainerConverter(Converter["Function"]):
    """ChainerConverter()


    """

    def __init__(self):
        super(ChainerConverter, self).__init__()

        if not FLAG_CHAINER_INSTALLED:
            raise ImportError("[ChainerConverter] Failed to import Chainer.")

    def convert_from_inout_vars(self, inputs: List["chainer.Variable"], outputs: List["chainer.Variable"]):
        """convert_from_inout_vars(inputs, output)

        Construct computational graph from input and output chainer variables, and convert the graph into WebDNN IR.

        Args:
            inputs(list of chainer.Variable): input chainer variables
            outputs(list of chainer.Variable): output chainer variables

        .. warning::

            This method will be removed in the future version. Use :func:`~webdnn.frontend.chainer.ChainerConverter.convert(inputs,
            outputs)`.

        .. admonition:: Example

            .. code::

                model = chainer.links.model.vision.resnet.ResNet50Layers()

                # Forward propagation with dummy input to build computational graph
                x = chainer.Variable(np.empty((1, 3, 224, 224), dtype=np.float32))
                y = model(x, layers=["fc6"])["fc6"]

                graph = ChainerConverter().convert_from_inout_vars([x], [y])

        Returns:
            (:class:`~webdnn.Graph`): WebDNN Graph
        """
        warnings.warn("This method will be removed in the future version. Use ChainerConverter#convert(inputs, outputs).",
                      DeprecationWarning)
        return self.convert(inputs, outputs)

    def convert(self, inputs: List["chainer.Variable"], outputs: List["chainer.Variable"]) -> Graph:
        """convert(inputs, outputs)

        Convert chainer computational graph into WebDNN IR.

        Args:
            inputs(list of chainer.Variable): input chainer variables
            outputs(list of chainer.Variable): output chainer variables

        .. admonition:: Example

            .. code::

                model = chainer.links.model.vision.resnet.ResNet50Layers()

                # Forward propagation with dummy input to build computational graph
                x = chainer.Variable(np.empty((1, 3, 224, 224), dtype=np.float32))
                y = model(x, layers=["fc6"])["fc6"]

                graph = ChainerConverter().convert_from_inout_vars([x], [y])

        Returns:
            (:class:`~webdnn.Graph`): WebDNN Graph
        """
        chainer_graph = chainer.computational_graph.build_computational_graph(outputs)

        # In chainer v2, variables are represented as Variable and VariableNode object, and
        # graph information such as edge connection is contained in variable node.
        # Therefore all chainer variable must be normalized into variable node.
        c_vars = list(map(_to_variable_node,
                          filter(lambda v: isinstance(v, VariableNode), chainer_graph.nodes)))  # type: List[VariableNode]
        inputs = [_to_variable_node(v) for v in inputs]
        outputs = [_to_variable_node(v) for v in outputs]
        input_set = set(inputs)

        for c_var in c_vars:
            if c_var.creator is None:
                # If :code:`creator is None` and it's not input variable, it's parameter.

                # NOTE(Kiikurage):
                # In chainer v1.x and v2.x, `Variable` doesn't support `__eq__` method and `list.__contains__` cannot be used for
                # Variable list. However, `Variable.__hash__` is implemented and `set.__contains__` is available.
                self._convert_var(c_var, constant=c_var not in input_set)

        for c_opr in _listup_functions(inputs, outputs):
            self._convert_operator(c_opr)

        graph = Graph([self.get_variable(c_var) for c_var in inputs],
                      [self.get_variable(c_var) for c_var in outputs])

        for v in graph.inputs:
            v.attributes.add(Input(v))

        for v in graph.outputs:
            v.attributes.add(Output(v))

        return graph

    def _convert_var(self, c_var: "VariableNode", constant=False):
        assert not self.has_variable(c_var), f"{c_var} is already converted"
        ndim = len(c_var.shape)
        order = Order([None] * ndim)

        if constant:
            data = c_var.data
            if chainer_v2 and data is None:
                # noinspection PyProtectedMember
                data = c_var._variable().data

            n_var = ConstantVariable(chainer.cuda.to_cpu(data), order)  # force on CPU

        else:
            n_var = Variable(c_var.shape, order)

        self.set_variable(c_var, n_var)
        return n_var
