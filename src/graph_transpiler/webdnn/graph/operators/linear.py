from typing import Optional

from webdnn.graph.axis import Axis
from webdnn.graph.operator import Operator
from webdnn.graph.order import OrderNC
from webdnn.graph.placeholder import Placeholder
from webdnn.graph.variable import Variable


class Linear(Operator):
    """Linear(name)

    Linear operator a.k.a. Dense, Fully-Connected operator.

    This operator compute dot product with input and weight variables. Except :obj:`~webdnn.Axis.N`, all axes are used for
    calculation. If x is :obj:`~webdnn.graph.order.OrderNC` and w is :obj:`~webdnn.graph.order.OrderCN`, this operation is just same as
    :code:`np.tensor_dot(x, w, (1, 0))` in numpy's :code:`tensordot`.

    Also, 4D variable is acceptable for input and weight variable. If x is :obj:`~webdnn.graph.order.OrderNCHW` and w is
    :obj:`~webdnn.graph.order.OrderNHWC`, this operation is just same as :code:`np.tensor_dot(x, w, ((1,2,3), (3,1,2))` in numpy's
    :code:`tensordot`.

    Input and weight variables must be same dimension. Otherwise, an assertion error is raised.

    Args:
        name (str): Operator name.

    Signature
        .. code::

            y, = op(x, w)

        - **x** - Input variable.
        - **w** - Weight variable.
        - **y** - Output variable. Its order is :obj:`~webdnn.graph.order.OrderNC`. Its :obj:`~webdnn.Axis.N` size is same as
          :code:`x.shape_dict[Axis.N]`, and its :obj:`~webdnn.Axis.C` size is same as :code:`w.shape_dict[Axis.N]`
    """

    def __init__(self, name: Optional[str]):
        super().__init__(name)

    def __call__(self, x: Variable, w: Variable):
        if Placeholder.check_resolved(x.shape_dict[Axis.C]) and Placeholder.check_resolved(w.shape_dict[Axis.C]):
            assert x.shape_dict[Axis.C] == w.shape_dict[Axis.C], "Input and Weight variable of Linear operator must have same shape " \
                                                                 "except Axis.N " \
                                                                 f"size: x.shape_dict[Axis.C]={x.shape_dict[Axis.C]}, " \
                                                                 f"size: w.shape_dict[Axis.C]={w.shape_dict[Axis.C]}"

        assert x.ndim == w.ndim, "Input and Weight variable of Linear operator must be same dimension: " \
                                 f"len(x.ndim)={x.ndim}, len(w.ndim)={w.ndim}"

        if x.ndim == 4:
            if Placeholder.check_resolved(x.shape_dict[Axis.H]) and Placeholder.check_resolved(w.shape_dict[Axis.H]):
                assert x.shape_dict[Axis.H] == w.shape_dict[Axis.H], "Input and Weight variable of Linear operator must have same shape " \
                                                                     "except Axis.N " \
                                                                     f"size: x.shape_dict[Axis.H]={x.shape_dict[Axis.H]}, " \
                                                                     f"size: w.shape_dict[Axis.H]={w.shape_dict[Axis.H]}"

            if Placeholder.check_resolved(x.shape_dict[Axis.W]) and Placeholder.check_resolved(w.shape_dict[Axis.W]):
                assert x.shape_dict[Axis.W] == w.shape_dict[Axis.W], "Input and Weight variable of Linear operator must have same shape " \
                                                                     "except Axis.N " \
                                                                     f"size: x.shape_dict[Axis.W]={x.shape_dict[Axis.W]}, " \
                                                                     f"size: w.shape_dict[Axis.W]={w.shape_dict[Axis.W]}"

        y = Variable([x.shape_dict[Axis.N], w.shape_dict[Axis.N]], OrderNC)

        self.append_input("x", x)
        self.append_input("w", w)
        self.append_output("y", y)
        return y,
