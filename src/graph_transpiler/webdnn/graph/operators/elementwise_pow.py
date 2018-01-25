from webdnn.graph.graph import Graph
from webdnn.graph.operators.elementwise import Elementwise
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.variables.constant_variable import ConstantVariable


class ElementwisePow(Elementwise):
    """ElementwisePow(name)

    Elementwise power

    Args:
        name (str): Operator name.

    Signature
        .. code::

            y, = op(x0, x1)

        - **x0**, **x1** - Input variable. They must be same shape.
        - **y** - Output variable. Its order and shape is same as :code:`x0`.

        This operator also can be called by :code:`**`.

        .. code::

            y = x0 ** x1
    """

    def fold_constance(self, graph: Graph):
        x0 = self.inputs["x0"]  # type: ConstantVariable
        x1 = self.inputs["x1"]  # type: ConstantVariable
        y = self.outputs["y"]
        self.remove_all()

        y_new = ConstantVariable(x0.data, x0.order).change_order(y.order)
        y_new.data = y_new.data ** ConstantVariable(x1.data, x1.order).change_order(y.order).data
        OptimizeRule.replace_variable(graph, y, y_new)
