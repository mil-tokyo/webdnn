from typing import Optional

from webdnn.graph.axis import Axis
from webdnn.graph.operator import Operator
from webdnn.graph.operators.attributes.tensorwise import Tensorwise
from webdnn.graph.variable import Variable


class Normalize(Operator):
    """Normalize(name, axis, eps)

    Operator same as normalization layer in Chainer. Does L2 normalization along specified axis.

    For more detail, see: https://docs.chainer.org/en/stable/reference/generated/chainer.functions.normalize.html#chainer.functions.normalize

    Args:
        name (str): Operator name.
        axis (:obj:`~webdnn.graph.axis.Axis`) : axis which will be reduced.
        eps (float): epsilon.


    Signature
        .. code::

            y, = op(x)

        - **x** - Input variable.
        - **y** - Output variable. Its order and shape is same as :code:`x`.
    """

    def __init__(self, name: Optional[str], axis: Axis, eps: float):
        super().__init__(name)
        self.parameters["axis"] = axis
        self.parameters["eps"] = eps

    def __call__(self, x: Variable):
        y = Variable(x.shape, x.order)

        self.append_input("x", x)
        self.append_output("y", y)
        return y,
