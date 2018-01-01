from typing import Optional, Union

from webdnn.graph.axis import AxisKeyDict
from webdnn.graph.graph import Graph
from webdnn.graph.operator import Operator
from webdnn.graph.operators.attributes.tensorwise import Tensorwise
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.order import Order
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable


def normalize_slice(s: slice, size: int):
    step = 1 if s.step is None else s.step
    start = (s.start if s.start >= 0 else s.start + size) if s.start is not None else (0 if step > 0 else size - 1)
    stop = (s.stop if s.stop >= 0 else s.stop + size) if s.stop is not None else (size if step > 0 else -1)

    return slice(start, stop, step)


class Slice(Operator):
    """Slice(name, indices)

    Slice original variable to sub variable.

    Args:
        name (str): Operator name.
        indices (:class:`AxisKeyDict` of slice, int, or None): slicing indices

    Signature
        .. code::

            y = x[indices]

        - **x** - Input variable.
        - **y** - Sliced variable.
    """

    def __init__(self, name: Optional[str], indices: AxisKeyDict[Union[slice, int, None]]):
        super().__init__(name)

        for axis, index in indices.items():
            if not (isinstance(index, (slice, int)) or index is None):
                raise TypeError(f"""
[Slice] Each index must be an instance of slice, int, or NoneType:
    (indices) = {indices}
    (type(indices[{axis.name}])) = {type(index)}
""")

        self.parameters["indices"] = indices

    def __call__(self, x: Variable):
        # assert index is valid
        for axis, index in self.indices.items():
            if axis in x.order.axes:
                if isinstance(index, slice):
                    index = normalize_slice(index, x.shape_dict[axis])

                    valid_start = -x.shape_dict[axis] <= index.start <= x.shape_dict[axis]
                    valid_stop = -x.shape_dict[axis] <= index.stop <= x.shape_dict[axis]
                    if not valid_start or not valid_stop:
                        raise ValueError(f"""
[Slice] Index {index} in {axis} is out of range:
    (x.order) = {x.order}
    (x.shape) = {x.shape}
    (indices) = {self.indices}
    (indices[{axis.name}]) = {index}
""")

                    if ((abs(index.stop - index.start) - 1) // abs(index.step)) + 1 < 0:
                        raise ValueError(f"""
[Slice] Slice operator doesn't support 0-size output:
    (x.order) = {x.order}
    (x.shape) = {x.shape}
    (indices) = {self.indices}
    (indices[{axis.name}]) = {index}
""")

                elif isinstance(index, int):
                    if not -x.shape_dict[axis] <= index < x.shape_dict[axis]:
                        raise ValueError(f"""
[Slice] Index {index} in {axis} is out of range:
    (x.order) = {x.order}
    (x.shape) = {x.shape}
    (indices) = {self.indices}
    (indices[{axis.name}]) = {index}
    (valid range) = [{-x.shape_dict[axis]}, {x.shape_dict[axis]})
""")

                elif index is None:
                    raise ValueError(f"""
[Slice] Axis {axis} is already exist:
    (x.order) = {x.order}
    (x.shape) = {x.shape}
    (indices) = {self.indices}
    (indices[{axis.name}]) = {index}
""")

            else:
                if index is not None:
                    raise ValueError(f"""
[Slice] Axis {axis} is not exist in input variable. In this case, index must be "None" (=insert new axis):
    (x.order) = {x.order}
    (x.shape) = {x.shape}
    (indices) = {self.indices}
    (indices[{axis.name}]) = {index}
""")

        if all(isinstance(index, int) for index in self.indices.values()):
            raise NotImplementedError(f"""
[Slice] Accessing to one element is not supported:
    (indices) = {self.indices}
""")

        y_shape_dict = AxisKeyDict()
        for axis, index in self.indices.items():
            if isinstance(index, slice):
                index = normalize_slice(index, x.shape_dict[axis])
                y_shape_dict[axis] = ((abs(index.stop - index.start) - 1) // abs(index.step)) + 1

            elif isinstance(index, int):
                pass  # Remove axis

            elif index is None:
                y_shape_dict[axis] = 1  # Insert axis

        y = Variable(list(y_shape_dict.values()), Order(list(y_shape_dict.keys())))

        for axis in x.order.axes:
            if axis in self.indices:
                index = self.indices[axis]
                if isinstance(index, slice) and index.start is None and index.stop is None and index.step is None:
                    # This axis is not sliced.
                    self.attributes.add(Tensorwise(axis))

            else:
                # This axis is not sliced.
                self.attributes.add(Tensorwise(axis))

        self.append_input("x", x)
        self.append_output("y", y)
        return y,

    @property
    def indices(self) -> AxisKeyDict[Union[slice, int, None]]:
        return self.parameters["indices"]

    def fold_constance(self, graph: Graph):
        x = self.inputs["x"]  # type: ConstantVariable
        y = self.outputs["y"]

        remained_axes_in_x_order = [a for a in x.order.axes if a in y.order.axes]
        new_axes = [a for a in y.order.axes if a not in x.order.axes]
        slices = [self.indices[a] for a in x.order.axes] + [None] * len(new_axes)

        new_y = ConstantVariable(x.data[slices], Order(remained_axes_in_x_order + new_axes))
        new_y.change_order(y.order)
        OptimizeRule.replace_variable(graph, y, new_y)
        self.remove_all()
