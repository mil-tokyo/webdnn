from typing import Optional

from webdnn.graph import graph
from webdnn.graph.operator import Operator
from webdnn.graph.operators.attributes.inplace import InplaceOperator
from webdnn.graph.operators.attributes.tensorwise import Tensorwise
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.order import Order
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable


class ReinterpretAxis(Operator):
    """ReinterpretAxis(name, in_order, out_order)

    Re-interpret an axis as another semantics. Shape is not changed.

    In case of :code:`in_order` is :obj:`~webdnn.graph.order.OrderNC` and :code:`out_order` is :obj:`~webdnn.graph.order.OrderNT`,
    if :obj:`~webdnn.graph.order.OrderCN` variable is input, `~webdnn.graph.order.OrderTN` variable is output.

    Args:
        name (str): Operator name.
        in_order (:class:`~webdnn.Order`): Input order
        out_order (:class:`~webdnn.Order`): Output order

    Signature
        .. code::

            y, = op(x)

        - **x** - Input variable.
        - **y** - Output variable. Its shape is same as :code:`x`.
    """

    def __init__(self, name: Optional[str], in_order: Order, out_order: Order):
        super().__init__(name)

        self.parameters["in_order"] = in_order
        self.parameters["out_order"] = out_order
        assert in_order.ndim == out_order.ndim, f"""
[ReinterpretAxis] Parameter "in_order" and "out_order" must have same number of dimension.
    (in_order) = {in_order}
    (out_order) = {out_order}"""
        self.attributes.add(InplaceOperator(self, "x", "y"))

    def __call__(self, x: Variable):
        assert self.in_order.check_same_axes(x.order), f"""
[ReinterpretAxis] Order mismatch:
    (op.in_order) = {self.in_order}
    (x.order) = {x.order}"""

        y = Variable(x.shape, Order([self.out_order.axes[self.in_order.axes_dict[a]] for a in x.order.axes]))

        for axis in x.order.axes:
            self.attributes.add(Tensorwise(axis))

        self.append_input("x", x)
        self.append_output("y", y)
        return y,

    def fold_constance(self, graph: "graph.Graph"):
        x = self.inputs["x"]  # type: ConstantVariable
        y = self.outputs["y"]
        self.remove_all()

        y_new = ConstantVariable(x.data, Order([self.out_order.axes[self.in_order.axes.index(a)] for a in x.order.axes]))
        OptimizeRule.replace_variable(graph, y, y_new.change_order(y.order))

    @property
    def in_order(self) -> Order:
        return self.parameters["in_order"]

    @property
    def out_order(self) -> Order:
        return self.parameters["out_order"]
