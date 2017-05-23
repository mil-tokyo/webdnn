from typing import Tuple

from webdnn.graph import traverse
from webdnn.graph.graph import Graph
from webdnn.graph.operators.attributes.elementwise import Elementwise
from webdnn.graph.operators.elu import Elu
from webdnn.graph.operators.relu import Relu
from webdnn.graph.operators.tanh import Tanh
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.variable import Variable


# FIXME
class CombineElementwiseOperation(OptimizeRule):
    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        return graph, False
        # matches = traverse.search_sub_structure(graph, [PostElementwise, Variable, Elementwise])
        # flag_changed = False
        #
        # for match in matches:
        #     op1 = match[0]
        #     op2 = match[2]
        #     x = list(op2.inputs.values())[0]
        #     y = list(op2.outputs.values())[0]
        #
        #     if isinstance(op2, Relu):
        #         op1.parameters["inline_elementwise"] = lambda exp: f"({exp}>0?{exp}:0)"
        #
        #     elif isinstance(op2, Elu):
        #         op1.parameters["inline_elementwise"] = lambda exp: f"({exp}>0?{exp}:(exp({exp})-1))"
        #
        #     elif isinstance(op2, Tanh):
        #         op1.parameters["inline_elementwise"] = lambda exp: f"(tanh({exp}))"
        #
        #     else:
        #         continue
        #
        #     op2.remove_all()
        #     op1.replace_output(x, y)
        #
        #     flag_changed = True
        #
        # return graph, flag_changed


class OptimizeElementwise(OptimizeRule):
    def __init__(self):
        super(OptimizeElementwise, self).__init__()

        self.register(CombineElementwiseOperation())
