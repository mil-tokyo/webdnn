from typing import List, Optional, Union

import numpy as np

from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.operator import Operator
from webdnn.graph.operators.attributes.tensorwise import Tensorwise
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.placeholder import Placeholder
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable


class Concat(Operator):
    """Concat(name, axis)

    Concatenate multiple variables into one variable along to specified axis.

    Args:
        name (str): Operator name.
        axis (:obj:~`webdnn.Axis`): target axis

    Signature
        .. code::

            y, = op(x0, x1, ...)

        - **x0**, **x1**, ... - Input variables. All variables has same shape except the specified axis.
        - **y** - Output variable. Its order is same as :code:`x0`.
    """

    def __init__(self, name: Optional[str], axis: Axis):
        super().__init__(name)
        self.parameters["axis"] = axis

    def __call__(self, *xs: Variable):
        axis = self.axis
        axis_index = xs[0].order.axes_dict[axis]
        axes = xs[0].order.axes

        y_shape = list(xs[0].shape)  # type: List[Union[int, Placeholder]]
        y_shape[axis_index] = 0
        y_order = xs[0].order

        for i, x in enumerate(xs):
            assert x.order.check_same_axes(xs[0].order), f"""
[Concat] Input variable of Concat operator must have same axes
  (x0.order.axes) = {xs[0].order.axes}
  (x{i}.order.axes) = {xs[i].order.axes}"""

            for other_axis in [other_axis for other_axis in axes if other_axis != axis]:
                if Placeholder.check_resolved(xs[0].shape_dict[other_axis]) and Placeholder.check_resolved(x.shape_dict[other_axis]):
                    assert xs[0].shape_dict[other_axis] == x.shape_dict[other_axis], f"""
[Concat] Input variable of Concat operator must be same shape except the specified axis:
  (x0.shape_dict[{other_axis}]) = {xs[0].shape_dict[other_axis]}
  (x{i}.shape_dict[{other_axis}]) = {xs[i].shape_dict[other_axis]}"""

            y_shape[axis_index] += x.shape_dict[axis]

        for a in y_order.axes:
            if a == axis:
                continue

            self.attributes.add(Tensorwise(a))

        y = Variable(y_shape, y_order)

        for i, x in enumerate(xs):
            self.append_input(f"x{i}", x)
        self.append_output("y", y)
        return y,

    @property
    def axis(self) -> Axis:
        return self.parameters["axis"]

    def fold_constance(self, graph: Graph):
        xs = [self.inputs[f"x{i}"] for i in range(len(self.inputs))]  # type: List[ConstantVariable]
        y = self.outputs["y"]

        data = np.concatenate([ConstantVariable(x.data, x.order).change_order(y.order).data for x in xs], axis=y.order.axes_dict[self.axis])
        new_y = ConstantVariable(data, y.order)
        OptimizeRule.replace_variable(graph, y, new_y)
        self.remove_all()
