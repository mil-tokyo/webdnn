from webdnn.graph import traverse
from webdnn.graph.operators.split_axis import SplitAxis
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.variable import Variable
from webdnn.util import flags


class SimplifySplitAxis(OptimizeRule):
    """
    before)
                        +- v2
        v1 -{SplitAxis}-+                  +- v4
                        +- v3 -{SplitAxis}-+
                                           +- v5

    after)
                        +- v2
                        |
        v1 -{SplitAxis}-+- v4
                        |
                        +- v5
    """

    def flags(self):
        return [
            flags.optimize.OPTIMIZE,
            flags.optimize.SIMPLIFY_ELEMENTWISE
        ]

    def optimize(self, graph):
        flag_changed = False
        matches = traverse.search_sub_structure(graph, [SplitAxis, Variable, SplitAxis])

        while len(matches) > 0:
            op1, h, op2 = matches.pop()  # type: SplitAxis, Variable, SplitAxis

            if len(h.input_to) > 1:
                # `h` will be removed by this optimization
                continue

            if op1.axis != op2.axis:
                # These operations cannot be merged.
                continue

            flag_changed = True
            x = op1.inputs["x"]

            hs = [op1.outputs[f"y{i}"] for i in range(len(op1.outputs))]
            i_h = hs.index(h)

            original_ys = list(hs)
            new_sections = op1.sections

            original_ys.remove(h)
            section_offset = ([0] + op1.sections)[i_h]
            op2_sections = [0] + op2.sections
            for i in range(len(op2.outputs)):
                original_ys.insert(i_h + i, op2.outputs[f"y{i}"])
                new_sections.insert(i_h + i, section_offset + op2_sections[i])

            new_sections.remove(section_offset)

            op1.remove_all()
            op2.remove_all()

            new_ys = SplitAxis(None, axis=op1.axis, sections=new_sections)(x)

            for original_y, new_y in zip(original_ys, new_ys):
                OptimizeRule.replace_variable(graph, new_y.transpose_like(original_y), original_y)

            matches = traverse.search_sub_structure(graph, [SplitAxis, Variable, SplitAxis])

        return graph, flag_changed
