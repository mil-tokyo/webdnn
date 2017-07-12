# -*- coding:utf-8 -*-

"""
Chainer Link -> Graph object converters
Assuming Chainer 1.23 or 2.0
"""

from typing import List, Union

from webdnn.frontend.converter import Converter
from webdnn.graph import traverse
from webdnn.graph.graph import Graph
from webdnn.graph.operators.convolution2d import Convolution2D
from webdnn.graph.operators.deconvolution2d import Deconvolution2D
from webdnn.graph.operators.linear import Linear
from webdnn.graph.operators.reinterpret_axis import ReinterpretAxis
from webdnn.graph.order import OrderNC, OrderNCHW, OrderC, OrderNHWC, OrderCNHW, Order, OrderCN, OrderHWNC, OrderHWCN
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
        return chainer_variable


class ChainerConverter(Converter["chainer.Function"]):
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
        return self.convert(chainer_graph, inputs, outputs)

    def convert(self, chainer_computational_graph: "chainer.computational_graph.ComputationalGraph",
                input_c_vars: List["chainer.Variable"], output_c_vars: List["chainer.Variable"]) -> Graph:
        """convert(chainer_computational_graph, input_c_vars, output_c_vars)

        Convert chainer computational graph into WebDNN IR.

        Instead of using this method directly, you should use
        :func:`convert_from_inout_vars<webdnn.frontend.chainer.ChainerConverter.convert_from_inout_vars>`.

        Args:
            chainer_computational_graph(chainer.computational_graph.ComputationalGraph): chainer computational graph
            input_c_vars(list of chainer.Variable): input chainer variables
            output_c_vars(list of chainer.Variable): output chainer variables

        Returns:
            (:class:`~webdnn.Graph`): WebDNN Graph
        """
        # In chainer v2, variables are represented as Variable and VariableNode object, and
        # graph information such as edge connection is contained in variable node.
        # Therefore all chainer variable must be normalized into variable node.
        input_c_vars = [_to_variable_node(v) for v in input_c_vars]
        output_c_vars = [_to_variable_node(v) for v in output_c_vars]

        # Append InputVariable attribute to input variables
        input_n_vars = []
        for c_var in input_c_vars:
            n_var = self._convert_var(c_var)
            n_var.attributes.add(Input(n_var))
            input_n_vars.append(n_var)

        self._convert_weight_vars(chainer_computational_graph)

        pending_c_oprs = [c_opr for c_opr in chainer_computational_graph.nodes if
                          isinstance(c_opr, chainer.Function)]

        while len(pending_c_oprs) > 0:
            for c_opr in pending_c_oprs:
                if all(((self.has_variable(_to_variable_node(c_var))) for c_var in c_opr.inputs)):
                    # All input variables of the `cfunc` are converted, so this `c_opr` can be converted.
                    self._convert_operator(c_opr)
                    pending_c_oprs.remove(c_opr)
                    break  # for c_opr in pending_functions
            else:
                console.debug(pending_c_oprs)
                raise ValueError("Inputs to functions cannot be resolved.")

        # Append OutputVariable attribute to output variables
        output_n_vars = []
        for c_var in output_c_vars:
            if not self.has_variable(c_var):
                raise ValueError("Output variable is not generated by graph.")
            n_var = self.get_variable(c_var)
            n_var.attributes.add(Output)
            output_n_vars.append(n_var)

        graph = Graph(input_n_vars, output_n_vars)
        # Convert variable order into typical one in Chainer
        self._transpose_vars(graph)

        return graph

    def _convert_weight_vars(self, chainer_computational_graph: "chainer.computational_graph.ComputationalGraph"):
        # Convert chainer variable which has name (= which is trained parameter) into WebDNN Variable object

        # special case
        for c_var in chainer_computational_graph.nodes:

            # noinspection PyUnresolvedReferences
            if isinstance(c_var, chainer.functions.normalization.batch_normalization.BatchNormalizationFunction):
                # In chainer's BatchNormalization, mean and va (c_var.inputs[3] and c_var.inputs[4]) have no name, but
                # they are trainable parameters.
                if len(c_var.inputs) == 5:  # data, gamma, bias, mean, var
                    self._convert_var(c_var.inputs[3], force_constant=True)
                    self._convert_var(c_var.inputs[4], force_constant=True)

            elif isinstance(c_var, chainer.functions.connection.deconvolution_2d.Deconvolution2DFunction):
                # The order of weight of deconvolution2D in chainer is not Order NCHW, but OrderCNHW.
                self._convert_var(c_var.inputs[1], force_constant=True, force_order=OrderCNHW)

        # general case
        for c_var in chainer_computational_graph.nodes:
            if isinstance(c_var, VariableNode):
                if (not self.has_variable(c_var)) and c_var.name is not None:
                    self._convert_var(c_var)

    def _convert_var(self, c_var: "VariableNode", force_constant=False, force_order: Order = None):
        assert not self.has_variable(c_var), f"{c_var} is already converted"
        ndim = len(c_var.shape)
        if force_order:
            order = force_order

        else:
            if ndim == 4:
                # both weight and variable
                order = OrderNCHW
            elif ndim == 2:
                # both weight and variable
                order = OrderNC
            elif ndim == 1:
                # both weight and variable
                order = OrderC
            else:
                raise NotImplementedError(f"Unknown data format: {c_var}, ndim={c_var.ndim}, shape={c_var.shape}")

        assert order.ndim == ndim, f"Number of dimension is mismatched: order.ndim={order.ndim}, len(shape)={ndim}"

        if c_var.name is not None or force_constant:
            n_var = ConstantVariable(chainer.cuda.to_cpu(c_var.data), order)  # force on CPU
        else:
            n_var = Variable(c_var.shape, order)

        self.set_variable(c_var, n_var)
        return n_var

    # noinspection PyMethodMayBeStatic
    def _transpose_vars(self, graph: Graph):
        """
        Transpose variable order into typical WebDNN order.
        """
        for n_var in traverse.listup_variables(graph):
            if isinstance(n_var.output_from, ReinterpretAxis):
                # workaround for MatMulVarVar
                continue
            if isinstance(n_var, ConstantVariable):
                if n_var.ndim == 1:
                    n_var.change_order(OrderC)

                elif n_var.ndim == 2:
                    n_var.change_order(OrderCN)

                elif n_var.ndim == 4:
                    assert len(n_var.input_to) == 1
                    first_input_to = list(n_var.input_to)[0]

                    if isinstance(first_input_to, Convolution2D):
                        n_var.change_order(OrderHWNC)

                    elif isinstance(first_input_to, Deconvolution2D):
                        n_var.change_order(OrderHWNC)

                    elif isinstance(first_input_to, Linear):
                        n_var.change_order(OrderHWCN)

                    else:
                        raise NotImplementedError(f"Unknown data format: {n_var}")

            else:
                if n_var.ndim == 1:
                    n_var.change_order(OrderC)

                elif n_var.ndim == 2:
                    n_var.change_order(OrderNC)

                elif n_var.ndim == 4:
                    n_var.change_order(OrderNHWC)
