from typing import List, Set, Dict, Union

from torch.autograd import Variable as PTVariable, Function as PTFunction
from torch.autograd._functions.tensor import View as PTView
from torch.nn import Parameter as PTParameter
from torch.nn._functions.linear import Linear as PTLinear
# noinspection PyUnresolvedReferences
from torch.nn._functions.thnn.auto import Threshold as PTThreshold

from webdnn.graph.axis import Axis
from webdnn.graph.converters.converter import Converter
from webdnn.graph.graph import Graph
from webdnn.graph.operators.axiswise_bias import AxiswiseBias
from webdnn.graph.operators.flatten import Flatten
from webdnn.graph.operators.linear import Linear
from webdnn.graph.operators.relu import Relu
from webdnn.graph.order import Order, OrderNC, OrderC, OrderCN, OrderNCHW
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable


class PyTorchConverter(Converter[PTFunction, PTVariable]):
    def convert_variable_core(self, v: PTVariable, order: Order = None) -> Variable:
        ndim = len(v.size())
        # FIXME: This hard-coded default order may be wrong.
        if order is None:
            if ndim == 1:
                order = OrderC

            elif ndim == 2:
                order = OrderNC

            elif ndim == 4:
                order = OrderNCHW

            else:
                raise NotImplementedError(f"Unknown number of dimension: {ndim}")

        if isinstance(v, PTParameter):
            return ConstantVariable(v.data.numpy(), order)

        else:
            return Variable(list(v.size()), order)

    def convert_core(self, inputs: List[PTVariable], outputs: List[PTVariable]) -> Graph:
        stack = list(outputs)  # type: List[Union[PTFunction, PTVariable]]
        resolved = set()  # type: Set[Union[PTFunction, PTVariable]]
        queue = []  # type: List[Union[PTFunction, PTVariable]]

        # Traverse computation graph and list up nodes based on dependency order
        while len(stack) > 0:
            node = stack.pop()
            if node in resolved:
                continue

            if isinstance(node, PTVariable):
                unresolved = [node.creator] if ((node.creator is not None) and (node.creator not in resolved)) else []

            elif isinstance(node, PTFunction):
                unresolved = [fn[0] for fn in node.previous_functions if (fn[0] not in resolved)]

            else:
                # FIXME:
                # Some PyTorch Function is consisted separated forward and backward function objects.
                #
                # ex) BatchNormForward, BatchNormBackward,
                #     https://github.com/pytorch/pytorch/blob/v0.1.12/torch/csrc/autograd/functions/batch_normalization.cpp#L75-L82
                #
                # In this case, Variable#creator holds a reference to BACKWARD function object, not FORWARD function object.
                # Therefore, input variables of forward function cannot be detected, and traverse can't be continued.
                raise ValueError(f"Unknown node: type(node) == {type(node)}")

            if len(unresolved) > 0:
                stack.append(node)
                for fn in unresolved:
                    stack.append(fn)

            else:
                queue.append(node)
                resolved.add(node)

        inputs_table = {}  # type: Dict[Union[PTFunction, PTVariable], List[PTVariable]] # Dict[GraphNode, input_variables]
        outputs_table = {}  # type: Dict[Union[PTFunction, PTVariable], PTVariable] # Dict[GraphNode, output_variables]

        # Re-compute forward propagation to get references of hidden variables
        # FIXME: Pytorch may holds these references somewhere to use backward propagation, and re-computation may be not needed.
        for _ in outputs:
            queue.pop()

        last_fn = None
        while len(queue) > 0:
            node = queue.pop(0)
            last_fn = node
            if isinstance(node, PTVariable):
                outputs_table[node] = [node]
                continue

            elif isinstance(node, PTFunction):
                # FIXME: Support multiple outputs
                inputs_table[node] = [outputs_table[fn[0]][0] for fn in node.previous_functions]
                outputs_table[node] = [PTVariable(node.forward(*[v.data for v in inputs_table[node]]))]

        # Update outputs of graph
        outputs = outputs_table[last_fn]

        for fn in inputs_table.keys():
            self.convert_operator(fn, inputs_table[fn], outputs_table[fn])

        return Graph([self.convert_variable(v) for v in inputs],
                     [self.convert_variable(v) for v in outputs])


@PyTorchConverter.register_handler(PTLinear)
def _convert_linear(converter: Converter, _: PTLinear, inputs: List[PTVariable], outputs: List[PTVariable]):
    x = converter.convert_variable(inputs[0], OrderNC)
    w = converter.convert_variable(inputs[1], OrderNC)
    y = converter.convert_variable(outputs[0], OrderNC)

    w.change_order(OrderCN)

    linear = Linear(None)

    if len(inputs) == 3:
        b = converter.convert_variable(inputs[2], OrderC)
        bias = AxiswiseBias(None, axis=Axis.C)

        h, = linear(x, w)
        h, = bias(h, b)
        bias.replace_output(h, y)

    else:
        h, = linear(x, w)
        linear.replace_output(h, y)


@PyTorchConverter.register_handler(PTThreshold)
def _convert_threshold(converter: Converter, pt_fn: PTThreshold, inputs: List[PTVariable], outputs: List[PTVariable]):
    y = converter.convert_variable(outputs[0])
    x = converter.convert_variable(inputs[0], y.order)

    # https://github.com/pytorch/pytorch/blob/v0.1.12/torch/nn/modules/activation.py#L41
    threshold, value, is_inplace = pt_fn.additional_args

    if threshold == 0 and value == 0:  # ReLU
        relu = Relu(None)
        h, = relu(x)
        relu.replace_output(h, y)

    else:
        raise NotImplementedError("[PyTorchConverter] Threshold is supported only when threshold == 0 && value == 0 (=ReLU).")


@PyTorchConverter.register_handler(PTView)
def _convert_threshold(converter: Converter, pt_fn: PTView, inputs: List[PTVariable], outputs: List[PTVariable]):
    # https://github.com/pytorch/pytorch/blob/v0.1.12/torch/autograd/_functions/tensor.py#L94
    if len(pt_fn.sizes) == 2 and pt_fn.sizes[0] == inputs[0].size()[0]:
        # Flatten
        y = converter.convert_variable(outputs[0], OrderNC)
        x = converter.convert_variable(inputs[0], OrderNCHW)
        flatten = Flatten(None, in_axes=[Axis.C, Axis.H, Axis.W], out_axis=Axis.C)
        h, = flatten(x)
        flatten.replace_output(h, y)

    else:
        # Reshape
        raise NotImplementedError("[PyTorchConverter] Reshape is not implemented yet.")
