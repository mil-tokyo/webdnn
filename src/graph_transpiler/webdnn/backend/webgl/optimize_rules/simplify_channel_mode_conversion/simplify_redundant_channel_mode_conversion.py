from webdnn.backend.webgl.attributes.channel_mode import ChannelMode, ChannelModeEnum
from webdnn.backend.webgl.operators.convert_r_to_rgba import ConvertRtoRGBA
from webdnn.backend.webgl.operators.convert_rgba_to_r import ConvertRGBAtoR
from webdnn.graph import traverse
from webdnn.graph.graph import Graph
from webdnn.graph.operators.transpose import Transpose
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.variable import Variable


class SimplifyRedundantChannelModeConversion(OptimizeRule):
    def optimize(self, graph: Graph):
        flag_changed = False

        """
        before)
        
        v0[RGBA] -{ConvertRtoRGBA}- v1[RGBA]
        
        after)
        
        v0[RGBA] -{ConvertRGBAtoR}- v2[Order=v0.order][R] -{Transpose}- v3[Order=v1.order][R]-{ConvertRtoRGBA}- v1[RGBA] 
        """
        matches = traverse.search_sub_structure(graph, [Variable, ConvertRtoRGBA, Variable])
        while len(matches) > 0:
            v0, r2rgba, v1 = matches.pop()  # type: Variable, ConvertRtoRGBA, Variable
            if not (ChannelMode.get(v0) == ChannelMode.get(v1) == ChannelModeEnum.RGBA):
                continue

            flag_changed = True

            r2rgba.remove_all()

            v2, = ConvertRGBAtoR(None)(v0)
            v2.change_order(v0.order)

            v3, = Transpose(None)(v2)
            v3.change_order(v1.order)

            v1_new, = ConvertRtoRGBA(None)(v3)
            v1_new.change_order(v1.order)

            OptimizeRule.replace_variable(graph, v1_new, v1)

        """
        before)

        v0[R] -{ConvertRGBAtoR}- v1[R]

        after)

        v0[R] -{Transpose}- v1[R] 
        """
        matches = traverse.search_sub_structure(graph, [Variable, ConvertRGBAtoR, Variable])
        while len(matches) > 0:
            v0, rgba2r, v1 = matches.pop()  # type: Variable, ConvertRGBAtoR, Variable
            if not (ChannelMode.get(v0) == ChannelMode.get(v1) == ChannelModeEnum.R):
                continue

            flag_changed = True

            rgba2r.remove_all()

            v1_new, = Transpose(None)(v0)
            v1_new.change_order(v1.order)

            OptimizeRule.replace_variable(graph, v1_new, v1)

        return graph, flag_changed
