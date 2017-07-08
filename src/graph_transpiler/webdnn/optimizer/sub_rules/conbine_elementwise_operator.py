from typing import Tuple

from webdnn.graph.graph import Graph
from webdnn.graph.operators.elementwise import Elementwise
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.traverse import search_sub_structure
from webdnn.graph.variable import Variable


class CombineElementwiseOperator(OptimizeRule):
    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        flag_changed = False

        matches = search_sub_structure(graph, [Elementwise, Variable, Elementwise])
        while len(matches) > 0:
            match = matches.pop()
            op1 = match[0]  # type: Elementwise
            h = match[1]  # type: Variable
            op2 = match[2]  # type: Elementwise
            y = op2.outputs["y"]

            if h.input_to != {op2}:
                continue

            if len(op2.inputs) > 1:
                continue

            op = Elementwise(None)
            op1.replace(op)
            op1.replace_output(h, y)
            matches = search_sub_structure(graph, [Elementwise, Variable, Elementwise])

        return graph, flag_changed
