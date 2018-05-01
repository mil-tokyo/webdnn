from typing import NamedTuple, List, Sequence

from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.operator import Operator
from webdnn.graph.operators.concat import Concat
from webdnn.graph.operators.split_axis import SplitAxis
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.variable import Variable
from webdnn.util.assertion import UnexpectedAndPleaseReportError


class GraphVars(NamedTuple):
    inputs: List[Variable]
    hidden: List[Variable]
    outputs: List[Variable]


def split_tensorwise(graph: Graph, op: Operator, v: Variable, v_pair: Sequence[Variable], axis: Axis):
    s1 = v_pair[0].shape_dict[axis]
    s2 = v_pair[1].shape_dict[axis]
    xs = dict(op.inputs)
    ys = dict(op.outputs)
    op.remove_all()

    op_0 = op.copy()
    op_1 = op.copy()

    for key, x in xs.items():
        if x == v:
            x_0, x_1 = v_pair

        else:
            if axis in x.order.axes:
                x_0, x_1 = SplitAxis(None, axis=axis, sections=[s1])(x)

            else:
                # splitting is not occurred
                x_0 = x_1 = x

        op_0.append_input(key, x_0)
        op_1.append_input(key, x_1)

    for key, y in ys.items():
        if y == v:
            y_0, y_1 = v_pair

        else:
            if axis in y.order.axes:
                # TODO (Kiikurage)
                # Attribute attached to "y" is not copied to neither "y_0" or "y_1"
                y_0 = Variable([s1 if a == axis else y.shape_dict[a] for a in y.order.axes], y.order)
                y_1 = Variable([s2 if a == axis else y.shape_dict[a] for a in y.order.axes], y.order)
                y_new, = Concat(None, axis=axis)(y_0, y_1)
                OptimizeRule.replace_variable(graph, y, y_new)

            else:
                raise UnexpectedAndPleaseReportError

        op_0.append_output(key, y_0)
        op_1.append_output(key, y_1)
