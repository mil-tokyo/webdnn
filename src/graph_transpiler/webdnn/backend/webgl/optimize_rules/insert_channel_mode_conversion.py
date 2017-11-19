from typing import Tuple

from webdnn.backend.webgl.attributes.channel_mode import ChannelModeEnum, ChannelMode
from webdnn.backend.webgl.operators.convert_r_to_rgba import ConvertRtoRGBA, convert_r_to_rgba
from webdnn.backend.webgl.operators.convert_rgba_to_r import ConvertRGBAtoR, convert_rgba_to_r
from webdnn.graph import traverse
from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.operator import Operator
from webdnn.graph.operators.im2col import Im2Col
from webdnn.graph.operators.tensordot import Tensordot
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.variable import Variable


def _replace_input(op: Operator, var_name: str, target: ChannelModeEnum):
    """
    before)

        v -{op}-

    after)

        v -{conversion}- v' -{op}-
    """
    v = op.inputs[var_name]

    if ChannelMode.get(v) == target:
        return False

    if target == ChannelModeEnum.RGBA:
        v_new = convert_r_to_rgba(v)
    else:
        v_new = convert_rgba_to_r(v)
    op.replace_input(v, v_new)
    return True


def _replace_output(op: Operator, var_name: str, target: ChannelModeEnum):
    """
    before)

        -{op}- v

    after)

        -{op}- v' -{conversion}- v
    """
    v = op.outputs[var_name]

    if ChannelMode.get(v) == target:
        return False

    v_new = Variable(v.shape, v.order)
    ChannelMode.set(v_new, target)

    op.replace_output(v, v_new)
    if target == ChannelModeEnum.RGBA:
        convert_rgba_to_r(v_new).change_order(v.order).replace(v)
    else:
        convert_r_to_rgba(v_new).change_order(v.order).replace(v)
    return True


def _replace_input_all(op: Operator, target: ChannelModeEnum):
    return any(_replace_input(op, var_name, target) for var_name in op.inputs.keys())


def _replace_output_all(op: Operator, target: ChannelModeEnum):
    return any(_replace_output(op, var_name, target) for var_name in op.outputs.keys())


class InsertChannelModeConversion(OptimizeRule):
    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        flag_changed = False
        for op in traverse.listup_operators(graph):
            if isinstance(op, Tensordot):
                flag_changed |= _replace_output(op, "C", ChannelModeEnum.R)

            elif isinstance(op, Im2Col):
                flag_changed |= _replace_input(op, "im", ChannelModeEnum.R)
                if op.outputs["col"].shape_dict[Axis.C] % 4 == 0:
                    flag_changed |= _replace_output(op, "col", ChannelModeEnum.RGBA)
                else:
                    flag_changed |= _replace_output(op, "col", ChannelModeEnum.R)

            elif isinstance(op, ConvertRGBAtoR):
                flag_changed |= _replace_input(op, "x0", ChannelModeEnum.RGBA)
                flag_changed |= _replace_output(op, "y", ChannelModeEnum.R)

            elif isinstance(op, ConvertRtoRGBA):
                flag_changed |= _replace_input(op, "x0", ChannelModeEnum.R)
                flag_changed |= _replace_output(op, "y", ChannelModeEnum.RGBA)

            else:
                flag_changed |= _replace_input_all(op, ChannelModeEnum.R)
                flag_changed |= _replace_output_all(op, ChannelModeEnum.R)

        return graph, flag_changed
