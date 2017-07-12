from abc import ABCMeta
from typing import Optional

from webdnn.graph import variable
from webdnn.graph.operator import Operator
from webdnn.graph.operators.attributes.elementwise import Elementwise as ElementwiseAttribute
from webdnn.graph.operators.attributes.inplace import Inplace
from webdnn.graph.placeholder import Placeholder


class Elementwise(Operator, metaclass=ABCMeta):
    """Elementwise(name)
    Elementwise operator base class.

    Operation *"Elementwise"* is defined as follows:

    - It outputs only one variable.
    - All input variables and the output variable are same shape (not need to be same order).
    - Each element of output variable can be computed with only the elements at the same position of input variables.

      .. math::
        y[p] = f(x_0[p], x_1[p], ..., x_n[p]),

      where :math:`p` means the position of the element.

    All input variables are registered with name like :code:`x0`, :code:`x1`, ... :code:`x{index}`, and the output variable is registered
    with name :code:`y`.

    This operator has :obj:`~webdnn.graph.attributes.elementwise.Elementwise` attribute.

    Args:
        name (str): Operator name.

    Signature
        .. code::

            y, = op(x0, x1, ...)

        - **x0**, **x1**, ... - Input variables.
        - **y** - Output variable. Its shape and order is same as :code:`x0`.
    """

    def __init__(self, name: Optional[str]):
        super().__init__(name)

        # FIXME: attributes set may be overwritten in extended class's constructor
        self.attributes = {ElementwiseAttribute(self),
                           Inplace(self, "x0", "y")}

    def __call__(self, *xs: "variable.Variable"):
        y = variable.Variable(xs[0].shape, xs[0].order)
        for i, x in enumerate(xs):
            for axis in x.order.axes:
                assert axis in y.order.axes, f"All input variables of elementwise operator should be same shape. x[{i}] does not have " \
                                             f"{axis}: x0.order={xs[0].order}, x{i}.order={xs[i].order}"

                if Placeholder.check_resolved(x.shape_dict[axis]) or Placeholder.check_resolved(y.shape_dict[axis]):
                    assert y.shape_dict[axis] == x.shape_dict[axis], "All input variables of elementwise operator should be " \
                                                                     f"same shape: x0.shape_dict=f{xs[0].shape_dict}, x{i}" \
                                                                     f".shape_dict=f{xs[i].shape_dict}"

            self.append_input(f"x{i}", x)
        self.append_output("y", y)
        return y,
