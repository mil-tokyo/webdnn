from typing import Optional, List, Tuple

import numpy as np

from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.operator import Operator
from webdnn.graph.operators.attributes.tensorwise import Tensorwise
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable


class SplitAxis(Operator):
    """SplitAxis(name, sections, axis)

    Split variable along an axis

    Args:
        name (str): Operator name.
        sections (list of int): split positions
        axis (:class:`~webdnn.Axis`): axis

    Signature
        .. code::

            y0, y1, ... = op(x)

        - **x** - Input variable.
        - **y{n}** - Output variables.
    """

    def __init__(self, name: Optional[str], sections: List[int], axis: Axis):
        super().__init__(name)
        self.parameters["sections"] = list(sections)
        self.parameters["axis"] = axis

    def __call__(self, x: Variable):
        axis = self.parameters["axis"]
        sections = [0] + self.parameters["sections"] + [x.shape_dict[axis]]
        ys = []  # type: List[Tuple[str, Variable]]

        for i, i_from in enumerate(sections[:-1]):
            i_to = sections[i + 1]
            assert i_from < i_to, f"[SplitAxis] sections must be sorted ascending order: sections={sections}, sections[{i}]={i_from}, " \
                                  f"sections[{i+1}]={i_to}"

            out_shape = list(x.shape)
            out_shape[x.order.axes_dict[axis]] = i_to - i_from
            y = Variable(out_shape, x.order)

            ys.append((f"y{i}", y))

        for a in x.order.axes:
            if a == axis:
                continue

            self.attributes.add(Tensorwise(a))

        self.append_input(f"x", x)
        for key, y in ys:
            self.append_output(key, y)

        return tuple(y for _, y in ys)

    @property
    def axis(self) -> Axis:
        return self.parameters["axis"]

    @property
    def sections(self) -> List[int]:
        return list(self.parameters["sections"])

    def fold_constance(self, graph: Graph):
        x = self.inputs["x"]  # type: ConstantVariable
        ys = [self.outputs[f"y{i}"] for i in range(len(self.outputs))]
        axis = self.parameters["axis"]
        sections = self.parameters["sections"]

        self.remove_all()

        y_datum = np.split(x.data, sections, x.order.axes_dict[axis])
        for i, y in enumerate(ys):
            y_new = ConstantVariable(y_datum[i], x.order).change_order(y.order)
            OptimizeRule.replace_variable(graph, y, y_new)
