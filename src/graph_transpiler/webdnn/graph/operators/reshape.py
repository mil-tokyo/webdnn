from typing import Optional, List, Union

from webdnn.graph.operator import Operator
from webdnn.graph.operators.attributes.inplace import Inplace
from webdnn.graph.order import Order
from webdnn.graph.placeholder import Placeholder
from webdnn.graph.variable import Variable


class Reshape(Operator):
    """Reshape(name, in_order, out_order, out_shape)

    Reshape array assuming it is C-order.
    Removing / inserting axis with length 1

    When in_order: NHWC, out_order: NTC, out_shape: (2, 6, 10) and input variable is (2, 3, 4, 5), the semantic procedure is as follows.
    1. Interpret input variable as NTHWC (2, 1, 3, 4, 5) with inserting axis with length 1
    2. Reshape it with assuming C-order and length of axis being removed is 1; NTHWC (2, 6, 1, 1, 10)
    3. Remove axes; NTC (2, 6, 10)

    Swapping axes is prohibited because it is ambiguous.
    If in_order and out_order match the actual input / output variable order, kernel does not have to do anything.

    Args:
        name (str): Operator name.
        in_order (:class:`~webdnn.graph.order.Order`): input order
        out_order (:class:`~webdnn.graph.order.Order`): output order
        out_shape (list of int or :class:`~webdnn.graph.placeholder.Placeholder`): output shape

    Signature
        .. code::

            y, = op(x)

        - **x** - Input variable.
        - **y** - Output variable.
    """

    def __init__(self, name: Optional[str], in_order: Order, out_order: Order, out_shape: List[Union[int, Placeholder]]):
        super().__init__(name)

        self.parameters["in_order"] = in_order
        self.parameters["out_order"] = out_order
        assert -1 not in out_shape, "-1 (wildcard) in reshape output shape is currently not supported"
        self.parameters["out_shape"] = out_shape

        self.attributes.add(Inplace(self, "x", "y"))

    def __call__(self, x: Variable):
        assert self.parameters["in_order"] == x.order

        y = Variable(self.parameters["out_shape"], self.parameters["out_order"])
        assert y.shape == self.parameters[
            "out_shape"], f"Generated output shape does not match self.parameters[\"out_shape\"] " \
                          f"({y.shape} != {self.parameters['out_shape']})"
        self.append_input("x", x)
        self.append_output("y", y)

        return y,
