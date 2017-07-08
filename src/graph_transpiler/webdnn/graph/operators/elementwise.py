from abc import ABCMeta
from typing import Optional

from webdnn.graph import variable
from webdnn.graph.operator import Operator
from webdnn.graph.operators.attributes.elementwise import Elementwise as ElementwiseAttribute
from webdnn.graph.operators.attributes.inplace import Inplace
from webdnn.graph.placeholder import Placeholder


class Elementwise(Operator, metaclass=ABCMeta):
    """Elementwise operator base class

    Operation 'Elementwise' is defined as follows:

    - It outputs only one variable.

    - All input variables and the output variable are same shape.

    - For each element of output variable, it can be computed with only elements of input variable at same position of
      the output element.

        y[pos] = f(x0[pos], x1[pos], ..., x_n[pos])

    All input variables are registered with name like "x0", "x1", ... "x{index}". The output variable is registered with
    name "y".

    This operator has 2 attributes, `ElementwiseAttribute` and `Inplace(x0, y)`.

    Args:
        name (str): Operator name.
    """

    def __init__(self, name: Optional[str]):
        super().__init__(name)

        # FIXME: attributes set may be overwritten in extended class's constructor
        self.attributes = {ElementwiseAttribute(self),
                           Inplace(self, "x0", "y")}

    def __call__(self, *xs: "variable.Variable"):
        """
        Args:
            *xs (:class:`~webdnn.graph.variable.Variable`): Input variables. All input variables must be same shape.

        Returns:
            tuple of :class:`~webdnn.graph.variable.Variable`: Output variable. It is same shape of input variables.
        """
        y = variable.Variable(xs[0].shape, xs[0].order)
        for i, x in enumerate(xs):
            for axis in x.order.axes:
                assert axis in y.order.axes

                if Placeholder.check_resolved(x.shape_dict[axis]) or Placeholder.check_resolved(y.shape_dict[axis]):
                    assert y.shape_dict[axis] == x.shape_dict[axis]

            self.append_input(f"x{i}", x)
        self.append_output("y", y)
        return y,
