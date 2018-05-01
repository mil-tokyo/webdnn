from typing import NamedTuple, List, Sequence

from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.operators.concat import Concat
from webdnn.graph.operators.reshape import Reshape
from webdnn.graph.operators.split_axis import SplitAxis
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.variable import Variable
from webdnn.util.assertion import UnexpectedAndPleaseReportError
from webdnn.util.misc import mul


class GraphVars(NamedTuple):
    inputs: List[Variable]
    hidden: List[Variable]
    outputs: List[Variable]


def split_reshape(graph: Graph, op: Reshape, v: Variable, v_pair: Sequence[Variable], axis: Axis):
    x = op.inputs["x"]
    y = op.outputs["y"]
    s1 = v_pair[0].shape_dict[axis]
    s2 = v_pair[1].shape_dict[axis]
    op.remove_all()
    in_order = op.in_order
    out_order = op.out_order
    x_shape = [x.shape_dict[a] for a in in_order.axes]
    y_shape = [y.shape_dict[a] for a in out_order.axes]

    if v == x:
        """
        before)

            x -{reshape}- y

        after)

            x_0 -{reshape}- t_0 -+
                                 +-{concat[axis_k]}- t -{reshape}- y
            x_1 -{reshape}- t_1 -+

        shape and order is changed as follows:

                  x.shape = [dx_0, dx_1, ..., dx_m,   ..., dx_M-1]
                x_0.shape = [dx_0, dx_1, ..., dx_m/2, ..., dx_M-1]
            ---------------------------------------------------------------------------------
                t_0.shape = [dy_0, dy_1, ..., dy_n,   ..., dy_k/2, ..., dy_N-1]
                  t.shape = [dy_0, dy_1, ..., dy_n*2, ..., dy_k/2, ..., dy_N-1]
                  y.shape = [dy_0, dy_1, ..., dy_n,   ..., dy_k,   ..., dy_N-1]

            m: split target axis

            find axis_k and axis_n, which satisfies follow conditions

                dy_n * dy_n+1 * ... * dy_N-1 == dx_m * dx_m+1 * ... * dx_M-1
                dy_k % 2 == 0
                n <= k
        """

        x_0, x_1 = v_pair
        dx_prod = mul(x_shape[in_order.axes_dict[axis]:])
        dy_prod = 1
        axis_k_candidate = []
        for axis_n in reversed(out_order.axes):
            dy_prod *= y.shape_dict[axis_n]
            if y.shape_dict[axis_n] % 2 == 0:
                axis_k_candidate.append(axis_n)

            if dx_prod == dy_prod:
                # Split most large axis
                axis_k = (sorted(axis_k_candidate, key=lambda a: y.shape_dict[a], reverse=True))[0]

                t_0_shape = [y.shape_dict[a] for a in out_order.axes]
                t_0_shape[out_order.axes_dict[axis_k]] = t_0_shape[out_order.axes_dict[axis_k]] // 2  # TODO
                t_0, = Reshape(None, in_order=in_order, out_order=out_order, out_shape=t_0_shape)(x_0)

                t_1_shape = [y.shape_dict[a] for a in out_order.axes]
                t_1_shape[out_order.axes_dict[axis_k]] = t_1_shape[out_order.axes_dict[axis_k]] // 2  # TODO
                t_1, = Reshape(None, in_order=in_order, out_order=out_order, out_shape=t_1_shape)(x_1)

                t, = Concat(None, axis=axis_n)(t_0, t_1)
                y_new, = Reshape(None, in_order=out_order, out_order=out_order, out_shape=y_shape)(t)

                OptimizeRule.replace_variable(graph, y_new.transpose_like(y), y)
                break

            elif dy_prod > (s1 + s2) * dx_prod:
                raise NotImplementedError(f"Variable is too large to handle in WebGL backend: {v}")

    elif v == y:
        """
        algorithm is almost same as the case `v == x` (above).

        before)

            x -{reshape}- y

        after)

                                    +- t_0 -{reshape}- y_0
            x -{reshape}- t-{split}-+
                                    +- t_1 -{reshape}- y_1

        shape and order is changed as follows:

                  x.shape = [dx_0, dx_1, ..., dx_m,   ..., dx_k,   ..., dx_M-1]
                  t.shape = [dx_0, dx_1, ..., dx_m*2, ..., dx_k/2, ..., dx_M-1]
                t_0.shape = [dx_0, dx_1, ..., dx_m,   ..., dx_k/2, ..., dx_M-1]
            ---------------------------------------------------------------------------------
                y_0.shape = [dy_0, dy_1, ..., dy_n/2, ..., dy_N-1]
                  y.shape = [dy_0, dy_1, ..., dy_n,   ..., dy_N-1]

            m: split target axis

            find axis_k and axis_m, which satisfies follow conditions

                dx_m * dx_m+1 * ... * dx_M-1 == dy_n * dy_n+1 * ... * dy_N-1
                dx_k % 2 == 0
                m <= k
        """

        y_0, y_1 = v_pair
        dx_prod = 1
        dy_prod = mul(x_shape[out_order.axes_dict[axis]:])
        axis_k_candidate = []
        for axis_m in reversed(in_order.axes):
            dx_prod *= x.shape_dict[axis_m]
            if x.shape_dict[axis_m] % 2 == 0:
                axis_k_candidate.append(axis_m)

            if dx_prod == dy_prod:
                # Split most large axis
                axis_k = (sorted(axis_k_candidate, key=lambda a: x.shape_dict[a], reverse=True))[0]

                t_shape = [x.shape_dict[a] for a in in_order.axes]
                t_shape[in_order.axes_dict[axis_m]] = 2 * t_shape[in_order.axes_dict[axis_m]]  # TODO
                t_shape[in_order.axes_dict[axis_k]] = t_shape[in_order.axes_dict[axis_k]] // 2  # TODO
                t, = Reshape(None, in_order=in_order, out_order=in_order, out_shape=t_shape)(x)

                t_0, t_1 = SplitAxis(None, axis=axis_m, sections=[t.shape_dict[axis_m] // 2])(t)  # TODO

                y_0_new, = Reshape(None, in_order=in_order, out_order=out_order, out_shape=y_0.shape)(t_0)
                y_1_new, = Reshape(None, in_order=in_order, out_order=out_order, out_shape=y_1.shape)(t_1)

                OptimizeRule.replace_variable(graph, y_0_new.reshape_like(y_0), y_0)
                OptimizeRule.replace_variable(graph, y_1_new.reshape_like(y_1), y_1)
                break

            elif dx_prod > dy_prod:
                raise NotImplementedError(f"Variable is too large to handle in WebGL backend: {v}")

    else:
        raise UnexpectedAndPleaseReportError
