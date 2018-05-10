# -*- coding:utf-8 -*-

"""
Chainer Link -> Graph object converters
Assuming Chainer >=1.23-1.24, <5.0.0
"""
import traceback
import warnings
from typing import List, Union, Sequence, Dict, Tuple

import numpy as np

from webdnn.frontend.chainer.placeholder_variable import PlaceholderVariable
from webdnn.frontend.converter import Converter, CyclicGraphError
from webdnn.frontend.util import semver
from webdnn.graph.graph import Graph
from webdnn.graph.order import Order
from webdnn.graph.variable import Variable
from webdnn.graph.variables.attributes.input import Input
from webdnn.graph.variables.attributes.output import Output
from webdnn.graph.variables.constant_variable import ConstantVariable
from webdnn.util import console

# Function and type declarations (actual implementation is depend on installed Chainer version)

# T_FUNCTION: type of function node in computation graph
# T_VARIABLE: type of variable node in computation graph
T_NODE = Union["T_VARIABLE", "T_FUNCTION"]


def get_variable_data(variable: "T_VARIABLE") -> Union[np.ndarray, "chainer.cuda.ndarray"]: ...  # return variable's data


def to_variable_node(c_var: "chainer.Variable") -> "T_VARIABLE": ...  # convert "chainer.Variable" into variable node (T_VARIABLE instance)


FLAG_CHAINER_INSTALLED = False

try:
    import chainer
    import chainer.computational_graph

    VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH = semver(chainer.__version__)

    if VERSION_MAJOR >= 3:
        # v3.x.x
        if VERSION_MAJOR >= 5:
            warnings.warn(f"WebDNN does not support Chainer version >= 5. Currently, Chainer {chainer.__version__} is installed.")

        # In v3, Many functions are represented as instance of `chainer.function_node.FunctionNode`. However some functions are still
        # instance of `chainer.function.Function` (ex. Im2Col).
        T_FUNCTION = (chainer.FunctionNode, chainer.Function)
        T_VARIABLE = chainer.variable.VariableNode


        def get_variable_data(variable: T_VARIABLE):
            # noinspection PyProtectedMember
            return variable._variable().data if variable.data is None else variable.data


        def to_variable_node(c_var: chainer.Variable):
            return c_var.node

    elif VERSION_MAJOR == 2:
        # v2.x.x
        T_FUNCTION = chainer.Function
        T_VARIABLE = chainer.variable.VariableNode


        def get_variable_data(variable: T_VARIABLE):
            # noinspection PyProtectedMember
            return variable._variable().data if variable.data is None else variable.data


        def to_variable_node(c_var: chainer.Variable):
            return c_var.node

    elif (VERSION_MAJOR == 1) and (VERSION_MINOR >= 23):
        # v1.x.x
        T_FUNCTION = chainer.Function
        T_VARIABLE = chainer.Variable


        def get_variable_data(variable: T_VARIABLE):
            return variable.data


        def to_variable_node(c_var: chainer.Variable):
            return c_var

    else:
        raise NotImplementedError(f"WebDNN does not support Chainer older than v1.23. Currently, Chainer {chainer.__version__} is installed.")

    FLAG_CHAINER_INSTALLED = True

except Exception as e:
    console.warning(traceback.format_exc())


def _listup_functions(inputs: Sequence[T_NODE], outputs: Sequence[T_NODE]):
    input_set = set(inputs)

    def get_prev_nodes(node: T_NODE) -> Sequence[T_NODE]:
        # NOTE(Kiikurage):
        # In chainer v1, "Variable" doesn't support "__eq__" method, so "list.__contains__" cannot be used for list of variables.
        # However, "Variable.__hash__" is implemented and "set.__contains__" is available.
        if node in input_set:
            return []

        elif isinstance(node, T_VARIABLE):
            return [] if node.creator is None else [node.creator]

        else:
            return node.inputs

    result = []  # type: List[T_FUNCTION]
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
            if isinstance(node_from, T_FUNCTION):
                result.append(node_from)

            if node_to is not None:
                dependency_count[node_to] -= 1

        else:
            raise CyclicGraphError("[ChainerConverter] Cycles are detected, but ChainerConverter cannot convert cyclic graph")

    return result


class ChainerConverter(Converter["T_FUNCTION"]):
    """ChainerConverter()

    Converter for `Chainer <https://chainer.org/>`_.

    Currently, from :code:`v1.23` to :code:`v4.0.0` is supported.
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

        .. admonition:: example

            Convert pre-trained ResNet model

            .. code::

                model = chainer.links.model.vision.resnet.ResNet50Layers()

                # Forward propagation with dummy input to build computational graph
                x = chainer.Variable(np.empty((1, 3, 224, 224), dtype=np.float32))
                y = model(x, layers=["fc6"])["fc6"]

                graph = ChainerConverter().convert([x], [y])

        Returns:
            (:class:`~webdnn.Graph`): WebDNN Graph
        """

        for v in inputs:
            if isinstance(v, PlaceholderVariable):
                n_var = Variable(v.actual_shape, Order([None] * v.ndim))
                self.set_variable(to_variable_node(v), n_var)

        inputs = [to_variable_node(v) for v in inputs]
        outputs = [to_variable_node(v) for v in outputs]

        # Convert parameters into constant variable
        input_set = set(inputs)
        for node in chainer.computational_graph.build_computational_graph(outputs).nodes:
            if isinstance(node, T_VARIABLE) and not self.has_variable(node) and node.creator is None:
                # If "c_var.creator" is None, it's input variable or parameters.

                # NOTE(Kiikurage):
                # In chainer v1, "Variable" doesn't support "__eq__" method, so "list.__contains__" cannot be used for list of variables.
                # However, "Variable.__hash__" is implemented and "set.__contains__" is available.
                self._convert_var(node, constant=node not in input_set)

        # Convert each Chainer function into WebDNN operators
        for c_opr in _listup_functions(inputs, outputs):
            self._convert_operator(c_opr)

        # Build graph
        graph = Graph([self.get_variable(c_var) for c_var in inputs], [self.get_variable(c_var) for c_var in outputs])

        for v in graph.inputs:
            v.attributes.add(Input())

        for v in graph.outputs:
            v.attributes.add(Output())

        return graph

    def _convert_var(self, c_var: T_VARIABLE, constant=False):
        assert not self.has_variable(c_var), f"{c_var} is already converted"
        ndim = len(c_var.shape)
        order = Order([None] * ndim)

        if constant:
            data = get_variable_data(c_var)
            n_var = ConstantVariable(chainer.cuda.to_cpu(data), order)  # force on CPU

        else:
            n_var = Variable(c_var.shape, order)

        self.set_variable(c_var, n_var)
        return n_var
