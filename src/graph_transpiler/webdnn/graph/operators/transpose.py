from webdnn.graph.graph import Graph
from webdnn.graph.operators.elementwise import Elementwise
from webdnn.graph.optimize_rule import OptimizeRule


# FIXME: improve documentation


class Transpose(Elementwise):
    """Transposition. Doing nothing in frontend level,
    and do memory transposition in backend if input / output variable order differs.
    This layer is inserted in optimizer to support layers which accepts certain order.

    Args:
        name (str): Operator name.
    """

    def fold_constance(self, graph: Graph):
        x0 = self.inputs["x0"]
        y = self.outputs["y"]

        OptimizeRule.replace_variable(graph, y, x0.copy().change_order(y.order))
        self.remove_all()
