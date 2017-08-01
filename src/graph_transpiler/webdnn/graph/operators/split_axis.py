from typing import Optional, List

from webdnn.graph.axis import Axis
from webdnn.graph.operator import Operator
from webdnn.graph.variable import Variable


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
        self.append_input(f"x", x)

        axis = self.parameters["axis"]
        sections = [0] + self.parameters["sections"] + [x.shape_dict[axis]]
        outputs = []

        for i, i_from in enumerate(sections[:-1]):
            i_to = sections[i + 1]
            assert i_from < i_to, f"[SplitAxis] sections must be sorted ascending order: sections={sections}, sections[{i}]={i_from}, " \
                                  f"sections[{i+1}]={i_to}"

            out_shape = list(x.shape)
            out_shape[x.order.axes_dict[axis]] = i_to - i_from
            y = Variable(out_shape, x.order)

            outputs.append(y)
            self.append_output(f"y{i}", y)

        return outputs
