from webdnn.graph.operators.elementwise import Elementwise
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

    def fold_constance(self):
        x0 = self.inputs["x0"]  # type: ConstantVariable
        x1 = self.inputs["x1"]  # type: ConstantVariable
        y = self.outputs["y"]  # type: ConstantVariable

        y.replace(ConstantVariable(x0.copy().change_order(y.order).data ** x1.copy().change_order(y.order).data, y.order))
        self.remove_all()
