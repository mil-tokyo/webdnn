from typing import Optional

from webdnn.graph.axis import Axis
from webdnn.graph.operator import Operator
from webdnn.graph.operators.attributes.inplace import InplaceOperator
from webdnn.graph.variable import Variable


class Softmax(Operator):
    """Softmax(name, axis)

    Softmax operator.

    Args:
        name (str): Operator name.
        axis (:obj:`~webdnn.Axis`) axis operator computes along to.

    Signature
        .. code::

            y, = op(x)

        - **x0** - Input variable.
        - **y** - Output variable. Its order and shape is same as :code:`x0`.
    """

    def __init__(self, name: Optional[str], axis: Axis):
        super().__init__(name)
        self.parameters["axis"] = axis
        self.attributes.add(InplaceOperator(self, "x", "y"))

    def __call__(self, x: Variable):
        y = Variable(x.shape, x.order)

        self.append_input("x", x)
        self.append_output("y", y)
        return y,
