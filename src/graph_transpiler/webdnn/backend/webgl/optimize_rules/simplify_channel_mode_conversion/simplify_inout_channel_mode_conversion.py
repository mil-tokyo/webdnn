from webdnn.backend.webgl.operators.convert_r_to_rgba import ConvertRtoRGBA
from webdnn.backend.webgl.operators.convert_rgba_to_r import ConvertRGBAtoR
from webdnn.graph.graph import Graph
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.util import flags


class SimplifyInOutChannelModeConversion(OptimizeRule):
    """
    remove channel mode conversion for input and output variable of graph.
    """

    def flags(self):
        return [
            flags.optimize.OPTIMIZE,
            flags.optimize.SIMPLIFY_IN_OUT_CHANNEL_MODE_CONVERSION
        ]

    def optimize(self, graph: Graph):
        flag_changed = False

        for x in graph.inputs:
            if len(x.input_to) != 1:
                continue

            op = list(x.input_to)[0]
            if isinstance(op, ConvertRGBAtoR) or isinstance(op, ConvertRtoRGBA):
                flag_changed = True
                y = op.outputs["y"]
                op.remove_all()
                OptimizeRule.replace_variable(graph, x, y)

        for y in graph.outputs:
            if isinstance(y.output_from, ConvertRGBAtoR) or isinstance(y.output_from, ConvertRtoRGBA):
                flag_changed = True

                x = y.output_from.inputs["x0"]
                i = graph.outputs.index(y)
                graph.outputs.remove(y)
                graph.outputs.insert(i, x)

                if len(y.input_to) == 0:
                    y.output_from.remove_all()

        return graph, flag_changed
