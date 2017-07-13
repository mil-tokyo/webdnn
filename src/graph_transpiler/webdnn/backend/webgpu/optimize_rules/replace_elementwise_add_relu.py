from typing import Tuple

from webdnn.graph import traverse
from webdnn.graph.graph import Graph
from webdnn.graph.operators.elementwise_add import ElementwiseAdd
from webdnn.graph.operators.elementwise_add_relu import ElementwiseAddRelu
from webdnn.graph.operators.relu import Relu
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.variable import Variable


class ReplaceElementwiseAddRelu(OptimizeRule):
    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        matches = traverse.search_sub_structure(graph, [ElementwiseAdd, Variable, Relu])
        flag_changed = False
        while len(matches) > 0:
            match = matches.pop()

            op1 = match[0]  # type:ElementwiseAdd
            op2 = match[2]  # type:Relu

            x0 = op1.inputs["x0"]
            x1 = op1.inputs["x1"]
            y = op2.outputs["y"]

            op1.remove_all()
            op2.remove_all()

            dummy_y, = ElementwiseAddRelu(None)(x0, x1)
            dummy_y.replace(y)
            flag_changed = True
            matches = traverse.search_sub_structure(graph, [ElementwiseAdd, Variable, Relu])

        return graph, flag_changed
