from typing import Tuple

from graph_builder.graph.operator import Operator
from graph_builder.graph.operators.attributes.elementwise import Elementwise
from graph_builder.graph.operators.attributes.post_elementwise import PostElementwise
from graph_builder.graph.operators.elu import Elu
from graph_builder.graph.operators.relu import Relu
from graph_builder.graph.operators.tanh import Tanh
from graph_builder.optimizer import util
from graph_builder.optimizer.optimize_rule import OptimizeRule
from graph_builder.optimizer.optimizer import Optimizer


class CombineElementwiseOperation(OptimizeRule):
    def __call__(self, graph: Operator) -> Tuple[Operator, bool]:
        matches = util.search_sub_structure(graph, [PostElementwise, Elementwise])
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
            x.merge(y)
            flag_changed = True

        return graph, flag_changed


class OptimizeElementwise(Optimizer):
    def __init__(self):
        super(OptimizeElementwise, self).__init__()

        self.register(CombineElementwiseOperation())
