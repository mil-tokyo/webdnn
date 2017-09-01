from abc import ABCMeta
from typing import Optional

from webdnn.graph import variable
from webdnn.graph.axis import AxisKeyDict
from webdnn.graph.operator import Operator
from webdnn.graph.operators.attributes.elementwise import Elementwise as ElementwiseAttribute
from webdnn.graph.operators.attributes.inplace import Inplace
from webdnn.graph.order import Order
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

        self.attributes.add(ElementwiseAttribute(self))
        self.attributes.add(Inplace(self, "x0", "y"))

    def __call__(self, *xs: "variable.Variable"):
        y_axes = []
        y_shape_dict = AxisKeyDict()
        # Check variable in descent order of the number of dimensions.
        # Without this, inputs (C, NC) produces output order CN.
        xs_order = [(i, x) for i, x in enumerate(xs)]
        xs_order.sort(key=lambda d: -d[1].ndim)

        for i, x in xs_order:
            for axis in x.order.axes:
                if axis in y_axes:
                    if y_shape_dict[axis] == 1:
                        # broadcast
                        y_shape_dict[axis] = x.shape_dict[axis]
                else:
                    y_axes.append(axis)
                    y_shape_dict[axis] = x.shape_dict[axis]

                if Placeholder.check_resolved(x.shape_dict[axis]):
                    if Placeholder.check_resolved(y_shape_dict[axis]):
                        assert y_shape_dict[axis] == x.shape_dict[axis] or x.shape_dict[axis] == 1, \
                            "All input variables of elementwise operator should be same shape: " \
                            f"y.shape_dict[{axis}]={y_shape_dict[axis]}, " \
                            f"x{i}.shape_dict[{axis}]={x.shape_dict[axis]}"
                    else:
                        y_shape_dict[axis] = x.shape_dict[axis]

            self.append_input(f"x{i}", x)

        y = variable.Variable([y_shape_dict[axis] for axis in y_axes], Order(y_axes))
        self.append_output("y", y)
        return y,
