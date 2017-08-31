from typing import Tuple

from webdnn.backend.webgl.attributes.channel_mode import ChannelMode, ChannelModeEnum, SupportedChannelMode
from webdnn.backend.webgl.operators.convert_r_to_rgba import ConvertRtoRGBA
from webdnn.backend.webgl.operators.convert_rgba_to_r import ConvertRGBAtoR
from webdnn.graph import traverse
from webdnn.graph.graph import Graph
from webdnn.graph.operator import Operator
from webdnn.graph.operators.elementwise_add import ElementwiseAdd
from webdnn.graph.operators.elementwise_div import ElementwiseDiv
from webdnn.graph.operators.elementwise_mul import ElementwiseMul
from webdnn.graph.operators.elementwise_pow import ElementwisePow
from webdnn.graph.operators.exp import Exp
from webdnn.graph.operators.leaky_relu import LeakyRelu
from webdnn.graph.operators.reinterpret_axis import ReinterpretAxis
from webdnn.graph.operators.relu import Relu
from webdnn.graph.operators.reshape import Reshape
from webdnn.graph.operators.scalar_add import ScalarAdd
from webdnn.graph.operators.scalar_affine import ScalarAffine
from webdnn.graph.operators.scalar_mul import ScalarMul
from webdnn.graph.operators.sigmoid import Sigmoid
from webdnn.graph.operators.softplus import Softplus
from webdnn.graph.operators.softsign import Softsign
from webdnn.graph.operators.tanh import Tanh
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.variable import Variable
from webdnn.util import flags

_rgba_support_operators = [
    # Elementwise
    ElementwiseAdd, ElementwiseDiv, ElementwiseMul, ElementwisePow, Exp, LeakyRelu, Relu, ScalarAdd, ScalarAffine,
    ScalarMul, Sigmoid, Softplus, Softsign, Tanh,

    # Other
    Reshape, ReinterpretAxis
]


class InitializeChannelMode(OptimizeRule):
    def flags(self):
        return [
            flags.optimize.OPTIMIZE,
            flags.optimize.OPTIMIZE_CHANNEL_MODE
        ]

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        global _rgba_support_operators
        flag_changed = False
        for node in traverse.listup_nodes(graph):
            if node.has_attribute(ChannelMode):
                continue

            if isinstance(node, ConvertRtoRGBA) or isinstance(node, ConvertRGBAtoR):
                continue

            flag_changed = True
            node.attributes.add(ChannelMode(node, ChannelModeEnum.R))

            if isinstance(node, Operator):
                node.attributes.add(SupportedChannelMode(node, ChannelModeEnum.R))

                if node.__class__ not in _rgba_support_operators:
                    continue

                variables = list(node.inputs.values()) + list(node.outputs.values())

                if not all(v.order == variables[0].order for v in variables):
                    continue
                if not all(v.shape == variables[0].shape for v in variables):
                    continue

                node.attributes.add(SupportedChannelMode(node, ChannelModeEnum.RGBA))

        return graph, flag_changed


class ChangeOperatorChannelModeToRGBA(OptimizeRule):
    def flags(self):
        return [
            flags.optimize.OPTIMIZE,
            flags.optimize.OPTIMIZE_CHANNEL_MODE
        ]

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        global _rgba_support_operators
        flag_changed = False
        for op in traverse.listup_operators(graph):
            if op.__class__ not in _rgba_support_operators:
                # This operator doesn't support RGBA mode
                continue

            if op.get_attribute(ChannelMode)[0].mode == ChannelModeEnum.RGBA:
                # This operator is configured as RGBA mode already
                continue

            y = list(op.outputs.values())[0]
            if any(x.shape != y.shape for x in op.inputs.values()):
                # FIXME: ブロードキャストがあるとRGBAは無理
                continue

            op.get_attribute(ChannelMode)[0].mode = ChannelModeEnum.RGBA

            for name, x in op.inputs.items():
                op.remove_input(x)
                x_converted, = ConvertRtoRGBA(None)(x)
                op.append_input(name, x_converted)

            for name, y in list(op.outputs.items()):
                y_dummy = Variable(y.shape, y.order)
                y_converted, = ConvertRGBAtoR(None)(y_dummy)
                for op2 in y.input_to:  # type: Operator
                    op2.replace_input(y, y_converted)
                y_dummy.replace(y)
                y.get_attribute(ChannelMode)[0].mode = ChannelModeEnum.RGBA

            flag_changed = True

        return graph, flag_changed


def _remove_convert_with_input(x: Variable):
    requested_mode = None
    for op in x.input_to:
        if isinstance(op, ConvertRtoRGBA):
            if requested_mode is ChannelModeEnum.R:
                return False

            requested_mode = ChannelModeEnum.RGBA

        elif isinstance(op, ConvertRGBAtoR):
            if requested_mode is ChannelModeEnum.RGBA:
                return False

            requested_mode = ChannelModeEnum.R

        else:
            return False

    if requested_mode is None:
        return False

    x.get_attribute(ChannelMode)[0].mode = requested_mode
    for op in list(x.input_to):
        y = list(op.outputs.values())[0]
        op.remove_all()
        y.replace(x)

    return True


class RemoveConvertWithInput(OptimizeRule):
    """
    Remove convertRGBAtoR and convertRtoRGBA with input variable
    """

    def flags(self):
        return [
            flags.optimize.OPTIMIZE,
            flags.optimize.OPTIMIZE_CHANNEL_MODE
        ]

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        flag_changed = False
        for v in graph.inputs:
            flag_changed |= _remove_convert_with_input(v)

        return graph, flag_changed


def _remove_redundant_conversion(v: Variable):
    if isinstance(v.output_from, ConvertRtoRGBA):
        if all([isinstance(op, ConvertRGBAtoR) for op in v.input_to]):
            v2 = v.output_from.inputs["x0"]
            v.output_from.remove_all()
            v2.replace(v)

            for op in v.input_to:
                v2 = op.outputs["y"]
                op.remove_all()
                v2.replace(v)

            v.get_attribute(ChannelMode)[0].mode = ChannelModeEnum.R
            return True

    elif isinstance(v.output_from, ConvertRGBAtoR):
        if all([isinstance(op, ConvertRtoRGBA) for op in v.input_to]):
            v2 = v.output_from.inputs["x0"]
            v.output_from.remove_all()
            v2.replace(v)

            for op in v.input_to:
                v2 = op.outputs["y"]
                op.remove_all()
                v2.replace(v)

            v.get_attribute(ChannelMode)[0].mode = ChannelModeEnum.RGBA
            return True

    return False


class RemoveRedundantConversion(OptimizeRule):
    """
    Remove converters which is joint from same one variable

    before)
       {op}--> v1 --{ConvertRGBAtoR}--> x(R) --{ConvertRtoRGBA}--> v2 --{op}

    after)
       {op}--> x(RGBA) --{op}
    """

    def flags(self):
        return [
            flags.optimize.OPTIMIZE,
            flags.optimize.OPTIMIZE_CHANNEL_MODE
        ]

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        flag_changed = False
        for v in traverse.listup_variables(graph):
            flag_changed |= _remove_redundant_conversion(v)

        return graph, flag_changed


class OptimizeChannelMode(OptimizeRule):
    def flags(self):
        return [
            flags.optimize.OPTIMIZE,
            flags.optimize.OPTIMIZE_CHANNEL_MODE
        ]

    def __init__(self):
        super(OptimizeChannelMode, self).__init__()
        self.register(InitializeChannelMode())
        self.register(ChangeOperatorChannelModeToRGBA())
        self.register(RemoveConvertWithInput())
        self.register(RemoveRedundantConversion())
