from webdnn.backend.webgl.operators.convert_r_to_rgba import ConvertRtoRGBA
from webdnn.backend.webgl.operators.convert_rgba_to_r import ConvertRGBAtoR
from webdnn.graph import traverse
from webdnn.graph.graph import Graph
from webdnn.graph.operators.transpose import Transpose
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.variable import Variable


class SimplifyNonsenseChannelModeConversion(OptimizeRule):
    def optimize(self, graph: Graph):
        flag_changed = False

        """
        before)
        
                       +-{r2rgba}- y -
        x -{rgba2r}- h +
                       +-
        
        after)

           +-{rgba2r}- h -
        x -+
           +-{Transpose}- y -
        """
        matches = traverse.search_sub_structure(graph, [Variable, ConvertRGBAtoR, Variable, ConvertRtoRGBA, Variable])
        while len(matches) > 0:
            x, rgba2r, h, r2rgba, y = matches.pop()  # type: Variable, ConvertRGBAtoR, Variable, ConvertRtoRGBA, Variable
            flag_changed = True

            r2rgba.remove_all()
            y_new, = Transpose(None)(x)
            y_new.change_order(y.order)
            OptimizeRule.replace_variable(graph, y_new, y)
            matches = traverse.search_sub_structure(graph, [Variable, ConvertRGBAtoR, Variable, ConvertRtoRGBA, Variable])

            if len(h.input_to) == 0:
                rgba2r.remove_all()

        matches = traverse.search_sub_structure(graph, [Variable, ConvertRtoRGBA, Variable, ConvertRGBAtoR, Variable])
        while len(matches) > 0:
            x, r2rgba, h, rgba2r, y = matches.pop()  # type: Variable, ConvertRtoRGBA, Variable, ConvertRGBAtoR, Variable
            flag_changed = True

            rgba2r.remove_all()
            y_new, = Transpose(None)(x)
            y_new.change_order(y.order)
            OptimizeRule.replace_variable(graph, y_new, y)
            matches = traverse.search_sub_structure(graph, [Variable, ConvertRtoRGBA, Variable, ConvertRGBAtoR, Variable])

            if len(h.input_to) == 0:
                r2rgba.remove_all()

        return graph, flag_changed
