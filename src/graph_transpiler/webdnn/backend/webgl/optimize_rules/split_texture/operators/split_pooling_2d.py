from typing import NamedTuple, List, Sequence

import numpy as np

from webdnn.graph.axis import Axis, AxisKeyDict
from webdnn.graph.graph import Graph
from webdnn.graph.operators.concat import Concat
from webdnn.graph.operators.pooling_2d import Pooling2D
from webdnn.graph.operators.slice import Slice
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.order import OrderNHWC
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable
from webdnn.util.assertion import UnexpectedAndPleaseReportError


class GraphVars(NamedTuple):
    inputs: List[Variable]
    hidden: List[Variable]
    outputs: List[Variable]


def split_pooling_2d(graph: Graph, op: Pooling2D, v: Variable, v_pair: Sequence[Variable], axis: Axis):
    s1 = v_pair[0].shape_dict[axis]
    x = op.inputs["x"]
    y = op.outputs["y"]
    op.remove_all()

    if v == x:
        x_0, x_1 = v_pair
        s, k, p = (op.SH, op.KH, op.PH) if axis == Axis.H else (op.SW, op.KW, op.PW)

        raise NotImplementedError

    elif v == y:
        y_0, y_1 = v_pair
        s, k, p = (op.SH, op.KH, op.PH) if axis == Axis.H else (op.SW, op.KW, op.PW)

        x_0_range = (0 * s - k // 2, (y_0.shape_dict[axis] - 1) * s + k)
        x_1_range = (y_0.shape_dict[axis] * s - k // 2, (y.shape_dict[axis] - 1) * s + k)

        indices = AxisKeyDict(OrderNHWC.axes, [slice(None) for _ in OrderNHWC.axes])

        indices_0 = AxisKeyDict(indices)
        indices_0[axis] = slice(max(x_0_range[0], 0), min(x_0_range[1], x.shape_dict[axis]))

        indices_1 = AxisKeyDict(indices)
        indices_1[axis] = slice(max(x_1_range[0], 0), min(x_1_range[1], x.shape_dict[axis]))

        x_0, = Slice(None, indices=indices_0)(x)
        x_1, = Slice(None, indices=indices_1)(x)

        if p > 0:
            data = ConstantVariable(np.zeros([p if a == axis else x.shape_dict[a] for a in x.order.axes]), x.order)
            x_0, = Concat(None, axis=axis)(data, x_0)
            x_1, = Concat(None, axis=axis)(x_1, data)

        op_0, op_1 = op.copy(), op.copy()
        new_padding = (0, op.PW) if axis == Axis.H else (op.PH, 0)
        op_0.parameters["padding"] = new_padding
        op_1.parameters["padding"] = new_padding

        y_0_new, = op_0(x_0)
        y_1_new, = op_1(x_1)

        OptimizeRule.replace_variable(graph, y_0_new.transpose_like(y_0), y_0)
        OptimizeRule.replace_variable(graph, y_1_new.transpose_like(y_1), y_1)

    else:
        raise UnexpectedAndPleaseReportError()
