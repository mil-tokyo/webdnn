from typing import Tuple

from graph_transpiler.graph import traverse
from graph_transpiler.graph.graph import Graph
from graph_transpiler.graph.operators.attributes.elementwise import Elementwise
from graph_transpiler.graph.operators.attributes.post_elementwise import PostElementwise
from graph_transpiler.graph.operators.elu import Elu
from graph_transpiler.graph.operators.relu import Relu
from graph_transpiler.graph.operators.tanh import Tanh
from graph_transpiler.graph.optimize_rule import OptimizeRule


class CombineElementwiseOperation(OptimizeRule):
    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        matches = traverse.search_sub_structure(graph, [PostElementwise, Elementwise])
        flag_changed = False

        for match in matches:
            op1 = match[0]
            op2 = match[1]
            x = list(op2.inputs.values())[0]
            y = list(op2.outputs.values())[0]

            if isinstance(op2, Relu):
                op1.parameters["inline_elementwise"] = lambda exp: f"({exp}>0?{exp}:0)"

            elif isinstance(op2, Elu):
                op1.parameters["inline_elementwise"] = lambda exp: f"({exp}>0?{exp}:(exp({exp})-1))"

            elif isinstance(op2, Tanh):
                op1.parameters["inline_elementwise"] = lambda exp: f"(tanh({exp}))"

            else:
                continue

            op2.remove_all()
            op1.replace_output(x, y)

            flag_changed = True

        return graph, flag_changed


class OptimizeElementwise(OptimizeRule):
    def __init__(self):
        super(OptimizeElementwise, self).__init__()

        self.register(CombineElementwiseOperation())
