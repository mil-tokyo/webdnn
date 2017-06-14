from typing import Optional

from webdnn.graph.operator import Operator
from webdnn.graph.operators.attributes.elementwise import Elementwise
from webdnn.graph.operators.attributes.inplace import Inplace
from webdnn.graph.place_holder import PlaceHolder
from webdnn.graph.variable import Variable


class ElementwiseSum(Operator):
    """Calculate elementwise sum of multiple input variables.

    Args:
        name (str): Operator name.
    """

    def __init__(self, name: Optional[str]):
        super().__init__(name)
        self.attributes = {Elementwise(self),
                           Inplace(self, "x0", "y")}

    def __call__(self, *xs: Variable):
        """
        Args:
            *xs (:class:`~webdnn.graph.variable.Variable`): Inputs

        Returns:
            tuple of :class:`~webdnn.graph.variable.Variable`: Output
        """
        y = Variable(xs[0].shape, xs[0].order)
        for i, x in enumerate(xs):
            for axis in x.order.axes:
                assert axis in y.order.axes

                if PlaceHolder.check_resolved(x.shape_dict[axis]) or PlaceHolder.check_resolved(y.shape_dict[axis]):
                    assert y.shape_dict[axis] == x.shape_dict[axis]

            self.append_input(f"x{i}", x)
        self.append_output("y", y)
        return y,
