# -*- coding:utf-8 -*-

"""
Chainer Link -> Graph object converters
Assuming Chainer 1.23-1.24 or 2.0
"""
import warnings
from typing import List, Union, Sequence, Set

from chainer import Function

from webdnn.frontend.constraints import AxisVar
from webdnn.frontend.converter import Converter
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

    if chainer.__version__ >= "2.":
        chainer_v2 = True
        # noinspection PyUnresolvedReferences
        VariableNode = chainer.variable.VariableNode
    else:
        chainer_v2 = False
        VariableNode = chainer.variable.Variable

    FLAG_CHAINER_INSTALLED = True

except ImportError as e:
    console.debug("Chainer is not completely installed.")
    pass


def _to_variable_node(chainer_variable: Union["chainer.Variable", "VariableNode"]) -> "VariableNode":
    if chainer_v2 and not isinstance(chainer_variable, VariableNode):
        # noinspection PyUnresolvedReferences
        return chainer_variable.node
    else:
        # noinspection PyTypeChecker
        return chainer_variable


def _listup_functions(inputs: Sequence["VariableNode"], outputs: Sequence["VariableNode"]):
    stack = list(outputs)  # type: List[Union[VariableNode, Function]]
    resolved = set(inputs)  # type: Set[Union[VariableNode, Function]]
    result = []  # type: List[Function]

    while len(stack) > 0:
        node = stack.pop()
        if node in resolved:
            continue

        if isinstance(node, VariableNode):
            prev_nodes = [] if node.creator is None else [node.creator]
        else:
            prev_nodes = node.inputs
        unresolved_prevs = [prev_node for prev_node in prev_nodes if prev_node not in resolved]

        if len(unresolved_prevs) == 0:
            resolved.add(node)
            if isinstance(node, Function):
                result.append(node)

        else:
            stack.append(node)
            stack += unresolved_prevs

    return result


class ChainerConverter(Converter["Function"]):
    """ChainerConverter()


    """

    def __init__(self):
        if not FLAG_CHAINER_INSTALLED:
            raise ImportError("ImportError is occurred when chainer is loaded.")

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
                # In chainer v1.x, `Variable` doesn't support `__eq__` method and `list.__contains__` cannot be used for
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
        order = Order([AxisVar() for _ in range(ndim)])

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
