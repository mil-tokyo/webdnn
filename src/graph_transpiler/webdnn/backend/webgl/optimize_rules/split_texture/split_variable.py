from typing import NamedTuple, List, Sequence

import numpy as np

from webdnn.backend.webgl.attributes.channel_mode import ChannelMode
from webdnn.backend.webgl.attributes.texture_shape import TextureShape
from webdnn.backend.webgl.operators.partial_im2col import PartialIm2Col
from webdnn.backend.webgl.optimize_rules.split_texture.check_texture_size import SplitTarget
from webdnn.graph import traverse
from webdnn.graph.axis import Axis, AxisKeyDict
from webdnn.graph.graph import Graph
from webdnn.graph.operator import Operator
from webdnn.graph.operators.attributes.tensorwise import Tensorwise
from webdnn.graph.operators.concat import Concat
from webdnn.graph.operators.im2col import Im2Col
from webdnn.graph.operators.pooling_2d import Pooling2D
from webdnn.graph.operators.reshape import Reshape
from webdnn.graph.operators.slice import Slice
from webdnn.graph.operators.split_axis import SplitAxis
from webdnn.graph.operators.tensordot import Tensordot
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.order import Order, OrderNHWC
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable
from webdnn.util import console
from webdnn.util.assertion import UnexpectedAndPleaseReportError
from webdnn.util.misc import mul


class GraphVars(NamedTuple):
    inputs: List[Variable]
    hidden: List[Variable]
    outputs: List[Variable]


class SplitVariable(OptimizeRule):
    def optimize(self, graph: Graph):
        flag_changed = False

        for v in traverse.filter_nodes(traverse.listup_variables(graph), SplitTarget):
            axis = _choose_split_axis(v)
            _split_axis(v, axis, graph)
            flag_changed = True

        return graph, flag_changed


def _split_axis(v: Variable, axis: Axis, graph):
    """
    split variable by specified axis
    """
    s1 = v.shape_dict[axis] // 2
    s2 = v.shape_dict[axis] - s1

    if isinstance(v, ConstantVariable):
        v_datum = np.split(v.data, [s1], v.order.axes_dict[axis])
        v1 = ConstantVariable(v_datum[0], v.order)
        v2 = ConstantVariable(v_datum[1], v.order)

    else:
        v1 = Variable([s1 if a == axis else v.shape_dict[a] for a in v.order.axes], v.order)
        v2 = Variable([s2 if a == axis else v.shape_dict[a] for a in v.order.axes], v.order)

    ops = list(v.input_to)
    if v.output_from is not None:
        ops += [v.output_from]

    for op in ops:
        if all(isinstance(v, ConstantVariable) for v in op.inputs.values()):
            op.fold_constance(graph)

        elif isinstance(op, Tensordot):
            # NOTE:
            # "_split_tensordot" must be called before "_split_tensorwise".
            #
            # Let consider follow case:
            #
            #   A.order = [Axis.X, Axis.Y]
            #   B.order = [Axis.Y, Axis.Z]
            #   C, = Tensordot(None, [Axis.Y, Axis.Z])(A, B)  # -> C.order = [Axis.X, Axis.Y]
            #
            # In this case, tensordot operator has "Tensorwise[X]" and "Tensorwise[Y]" attributes, because "Tensordot" operation is
            # tensorwise operation for each output axis. However, "Axis.Y" is also contained in reduced axes in "A". Therefore,
            # "_split_tensorwise" incorrectly split "A".
            #
            _split_tensordot(graph, op, v, [v1, v2], axis)

        elif Tensorwise.check_splittable(op, axis):
            _split_tensorwise(graph, op, v, [v1, v2], axis)

        elif isinstance(op, SplitAxis):
            _split_splitaxis(graph, op, v, [v1, v2], axis)

        elif isinstance(op, Concat):
            _split_concat(graph, op, v, [v1, v2], axis)

        elif isinstance(op, Im2Col):
            _split_im2col(graph, op, v, [v1, v2], axis)

        elif isinstance(op, PartialIm2Col):
            _split_partial_im2col(graph, op, v, [v1, v2], axis)

        elif isinstance(op, Reshape):
            _split_reshape(graph, op, v, [v1, v2], axis)

        elif isinstance(op, Pooling2D):
            _split_pooling_2d(graph, op, v, [v1, v2], axis)

        else:
            raise NotImplementedError(f"Variable is too large to handle in WebGL backend: {v}")


def _split_concat(graph: Graph, op: Concat, v: Variable, v_pair: Sequence[Variable], axis: Axis):
    s1 = v_pair[0].shape_dict[axis]
    xs = [op.inputs[key] for key in sorted([key for key in op.inputs.keys() if key.startswith("x")])]
    y = op.outputs["y"]
    op.remove_all()

    if v in xs:
        x_0, x_1 = v_pair

        if axis == op.axis:
            """
            before)
                x1 -+
                    |
                x2 -+-{concat}- y
                    |
                x3 -+

            after)
                x1 ---+
                      |
                x2_0 -+
                      +-{concat}- y
                x2_1 -+
                      |
                x3 ---+
            """
            i = xs.index(v)
            xs.pop(i)
            xs.insert(i + 0, x_0)
            xs.insert(i + 1, x_1)

            y_new, = Concat(None, axis=axis)(*xs)
            OptimizeRule.replace_variable(graph, y, y_new)

        else:
            """
            before)
                x1 -+
                    |
                x2 -+-{concat[op.axis]}- y
                    |
                x3 -+

            after)
                                  +- x1_0 -+
                x1 -{split[axis]}-+        |
                                  +- x1_1 -|-+
                                           | |
                x2_0 ----------------------+---{concat[op.axis]}- y_0 -+
                                           | |                         +-{concat[axis]}- y
                x2_1 ----------------------|-+-{concat[op.axis]}- y_1 -+
                                           | |
                                  +- x3_0 -+ |
                x3 -{split[axis]}-+          |
                                  +- x3_1 ---+
            """
            xs_0, xs_1 = zip(*[v_pair if x == v else SplitAxis(None, axis=axis, sections=[s1])(x) for x in xs])
            y_0, = Concat(None, axis=op.axis)(*xs_0)
            y_1, = Concat(None, axis=op.axis)(*xs_1)
            y_new, = Concat(None, axis=axis)(y_0, y_1)
            OptimizeRule.replace_variable(graph, y_new, y)

    elif v == y:
        y_0, y_1 = v_pair

        if axis == op.axis:
            """
            before)
                x1 -+
                    |
                x2 -+-{concat[axis=op.axis]}- y
                    |
                x3 -+

            after)
                x1 ------------------------------+
                                                 +-{concat[axis=axis]}- y_0
                                       +- y_0_1 -+
                x2 -{split[axis=axis]}-+
                                       +- y_1_0 -+
                                                 +-{concat[axis=axis]}- y_1
                x3 ------------------------------+
            """
            # find input variable which should be split

            total_size = 0
            xs_0 = []  # type: List[Variable]
            xs_1 = list(xs)  # type: List[Variable]
            for x in xs:
                xs_1.remove(x)
                xs_0.append(x)
                total_size += x.shape_dict[axis]

                if total_size == s1:
                    # splitting is not needed
                    #
                    # x0, x1, ..., xn, | xn+1, ..., xs[-1]
                    # <--------------> | <--------------->
                    #       y_0        |       y_1
                    break

                elif total_size > s1:
                    # this `x` must be split
                    #
                    #  x0, x1, ..., xn, ..., xs[-1]
                    # <-------------><------------->
                    #       y_0           y_1

                    xn_0, xn_1 = SplitAxis(None, axis=axis, sections=[s1 - (total_size - x.shape_dict[axis])])(x)
                    xs_0.remove(x)
                    xs_0.append(xn_0)
                    xs_1.insert(0, xn_1)
                    break

            if len(xs_0) > 1:
                y_0, = Concat(None, axis=axis)(*xs_0)
                y_0.change_order(v_pair[0].order)

            elif len(xs_0) == 1:
                y_0 = xs_0[0]

            else:
                raise UnexpectedAndPleaseReportError

            if len(xs_1) > 1:
                y_1, = Concat(None, axis=axis)(*xs_1)
                y_1.change_order(v_pair[1].order)

            elif len(xs_1) == 1:
                y_1 = xs_1[0]

            else:
                raise UnexpectedAndPleaseReportError

            OptimizeRule.replace_variable(graph, y_0, v_pair[0])
            OptimizeRule.replace_variable(graph, y_1, v_pair[1])

        else:
            """
            before)
                x1 -+
                    |
                x2 -+-{concat[op.axis]}- y
                    |
                x3 -+

            after)
                                  +- x1_0 -+
                x1 -{split[axis]}-+        |
                                  +- x1_1 ---+
                                           | |
                                  +- x2_0 -+-|-{concat[op.axis]}- y_0
                x2 -{split[axis]}-+        | |
                                  +- x2_1 ---+-{concat[op.axis]}- y_1
                                           | |
                                  +- x3_0 -+ |
                x3 -{split[axis]}-+          |
                                  +- x3_1 ---+

            """
            xs_0, xs_1 = zip(*[SplitAxis(None, axis=axis, sections=[s1])(x) for x in xs])

            y_new_0, = Concat(None, axis=op.axis)(*xs_0)
            y_new_1, = Concat(None, axis=op.axis)(*xs_1)

            OptimizeRule.replace_variable(graph, y_new_0, y_0)
            OptimizeRule.replace_variable(graph, y_new_1, y_1)

    else:
        raise UnexpectedAndPleaseReportError


def _split_splitaxis(graph: Graph, op: SplitAxis, v: Variable, v_pair: Sequence[Variable], axis: Axis):
    s1 = v_pair[0].shape_dict[axis]
    x = op.inputs["x"]
    ys = [op.outputs[f"y{i}"] for i in range(len(op.outputs))]
    sections = op.parameters["sections"]
    op.remove_all()

    if v == x:
        x_0, x_1 = v_pair
        if axis == op.axis:
            """
            before)
                                      +-y1
                                      |
                x -{split[axis=axis]}-+-y2
                                      |
                                      +-y3

            after)
                                        +- y1
                x_0 -{split[axis=axis]}-+
                                        +- y2_0 -+
                                                 +-{concat[axis=axis]}- y2
                                        +- y2_1 -+
                x_1 -{split[axis=axis]}-+
                                        +- y3
            """
            # find output variable which should be split ("y2" in above figure)

            total_size = 0
            ys_0 = []  # type: List[Variable]
            ys_1 = list(ys)  # type: List[Variable]
            for y in ys:
                ys_1.remove(y)

                if total_size + y.shape_dict[axis] == s1:
                    # splitting is not needed
                    #
                    #       x_0        |       x_1
                    # <--------------> | <--------------->
                    # y0, y1, ..., yn, | yn+1, ..., ys[-1]
                    ys_0.append(y)
                    break

                elif total_size + y.shape_dict[axis] > s1:
                    # this `y` must be split
                    #
                    #         x_0         |         x_1
                    # <-----------------> | <----------------->
                    #  y0, y1, ..., yn_0, | yn_1, ..., ys[-1]
                    #               <----------->
                    #                     yn

                    yn_0 = Variable([s1 - total_size if a == axis else y.shape_dict[a] for a in y.order.axes],
                                    y.order)
                    yn_1 = Variable([y.shape_dict[axis] - (s1 - total_size) if a == axis else y.shape_dict[a] for a in y.order.axes],
                                    y.order)
                    OptimizeRule.replace_variable(graph, Concat(None, axis=axis)(yn_0, yn_1)[0].change_order(y.order), y)
                    ys_0.append(yn_0)
                    ys_1.insert(0, yn_1)
                    break

                else:
                    ys_0.append(y)
                    total_size += y.shape_dict[axis]

            if len(ys_0) > 1:
                sections_0 = [0]
                for y in ys_0:
                    sections_0.append(sections_0[-1] + y.shape_dict[axis])
                sections_0.pop(0)
                sections_0.pop()

                for y_new, y in zip(SplitAxis(None, axis=axis, sections=sections_0)(x_0), ys_0):
                    y_new.change_order(y.order)
                    OptimizeRule.replace_variable(graph, y_new, y)

            elif len(ys_0) == 1:
                OptimizeRule.replace_variable(graph, ys_0[0], x_0)

            else:
                raise UnexpectedAndPleaseReportError

            if len(ys_1) > 1:
                sections_1 = [0]
                for y in ys_1:
                    sections_1.append(sections_1[-1] + y.shape_dict[axis])
                sections_1.pop(0)
                sections_1.pop()

                for y_new, y in zip(SplitAxis(None, axis=axis, sections=sections_1)(x_1), ys_1):
                    y_new.change_order(y.order)
                    OptimizeRule.replace_variable(graph, y_new, y)

            elif len(ys_1) == 1:
                OptimizeRule.replace_variable(graph, ys_1[0], x_1)

            else:
                raise UnexpectedAndPleaseReportError

        else:
            """
            before)
                                         +- y1
                                         |
                x -{split[axis=op.axis]}-+- y2
                                         |
                                         +- y3

            after)
                                               +--- y1_0 -+
                                               |          +-{concat[axis=axis]}- y1
                                               | +- y1_1 -+
                                               | |
                    x_0 -{split[axis=op.axis]}-+-|- y2_0 -+
                                               | |        +-{concat[axis=axis]}- y2
                    x_1 -{split[axis=op.axis]}---+- y2_1 -+
                                               | |
                                               +-|- y3_0 -+
                                                 |        +-{concat[axis=axis]}- y3
                                                 +- y3_1 -+
            """
            ys_0 = SplitAxis(None, axis=op.axis, sections=op.sections)(x_0)
            ys_1 = SplitAxis(None, axis=op.axis, sections=op.sections)(x_1)

            for y, y_0, y_1 in zip(ys, ys_0, ys_1):
                y_new, = Concat(None, axis=axis)(y_0, y_1)
                OptimizeRule.replace_variable(graph, y_new, y)

    elif v in ys:
        op.remove_all()

        if axis == op.axis:
            """
            before)
                           +- y1
                           |
                x -{split}-+- y2
                           |
                           +- y3

            after)
                           +- y1
                           |
                           +- y2_0
                x -{split}-+
                           +- y2_1
                           |
                           +- y3
            """
            target_i = ys.index(v)

            s_insert = (0 if target_i == 0 else sections[target_i - 1]) + s1
            new_sections = list(sections)
            new_sections.insert(target_i, s_insert)

            new_ys = SplitAxis(None, axis=axis, sections=new_sections)(x)
            for i, new_y in enumerate(new_ys):
                if i == target_i:
                    ys.pop(0)
                    y = v_pair[0]
                    new_y.change_order(y.order)
                    OptimizeRule.replace_variable(graph, y, new_y)

                elif i == target_i + 1:
                    y = v_pair[1]
                    new_y.change_order(y.order)
                    OptimizeRule.replace_variable(graph, y, new_y)

                else:
                    y = ys.pop(0)
                    new_y.change_order(y.order)
                    OptimizeRule.replace_variable(graph, y, new_y)

        else:
            """
            before)

                 y1 y2 y3      y1   y2   y3
                +--+--+--+    +--+ +--+ +--+
                |  :  :  |    |  | |  | |  |
                |  :  :  | => |  | |  | |  |
                |  :  :  |    |  | |  | |  |
                +--+--+--+    +--+ +--+ +--+

                                    +- y1
                                    |
                x -{split[op.axis]}-+- y2
                                    |
                                    +- y3

            after) split y2 into y2_0 and y2_1

                                                y1_0 y2_0 y3_0         y2_0
                                  +--+--+--+    +--+ +--+ +--+     y1  +--+  y3
              0 +--+--+--+    x_0 |  :  :  |    |  | |  | |  |    +--+ |  | +--+
                |  :  :  |        +--+--+--+    +--+ +--+ +--+    |  | +--+ |  |
             s1 +  +  +  + =>                =>                => +  +      +  +
                |  :  :  |        +--+--+--+    +--+ +--+ +--+    |  | +--+ |  |
                +--+--+--+    x_1 |  :  :  |    |  | |  | |  |    +--+ |  | +--+
                                  +--+--+--+    +--+ +--+ +--+         +--+
                    x                           y1_1 y2_1 y3_1         y2_1

                                                          +--- y1_0 -+
                                                          |          +-{concat[axis]}- y1
                                                          | +- y1_1 -+
                                                          | |
                                 +- x_0 -{split[op.axis]}-+-|------------------------- y2_0
                x -{split[axis]}-+                        | |
                                 +- x_1 -{split[op.axis]}---+------------------------- y2_1
                                                          | |
                                                          +-|- y3_0 -+
                                                            |        +-{concat[axis]}- y3
                                                            +- y3_1 -+
            """
            x_0, x_1 = SplitAxis(None, axis=axis, sections=[s1])(x)
            ys_0, = SplitAxis(None, axis=op.axis, sections=op.sections)(x_0)
            ys_1, = SplitAxis(None, axis=op.axis, sections=op.sections)(x_1)
            for y, y_0, y_1 in zip(ys, ys_0, ys_1):
                if y == v:
                    OptimizeRule.replace_variable(graph, y_0, v_pair[0])
                    OptimizeRule.replace_variable(graph, y_1, v_pair[1])

                else:
                    y_new, = Concat(None, axis=axis)(y_0, y_1)
                    OptimizeRule.replace_variable(graph, y_new, y)

    else:
        raise UnexpectedAndPleaseReportError


def _split_reshape(graph: Graph, op: Reshape, v: Variable, v_pair: Sequence[Variable], axis: Axis):
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


def _split_im2col(graph: Graph, op: Im2Col, v: Variable, v_pair: Sequence[Variable], axis: Axis):
    s1 = v_pair[0].shape_dict[axis]
    im = op.inputs["im"]
    col = op.outputs["col"]

    op.remove_all()

    if v == col:
        """
        before)

        im -{Im2Col}- col

        after)

                            +- col_0
        im -{PartialIm2Col}-+
                            +- col_1
        """
        col_0, col_1 = PartialIm2Col(None,
                                     ksize=op.ksize, stride=op.stride, padding=op.padding, dilation_rate=op.dilation_rate,
                                     axis=axis, sections=[s1])(im)

        OptimizeRule.replace_variable(graph, col_0.transpose(v_pair[0].order), v_pair[0])
        OptimizeRule.replace_variable(graph, col_1.transpose(v_pair[1].order), v_pair[1])

    elif v == im:
        raise NotImplementedError(f"Variable is too large to handle in WebGL backend: {v}")

    else:
        raise UnexpectedAndPleaseReportError


def _split_partial_im2col(graph: Graph, op: PartialIm2Col, v: Variable, v_pair: Sequence[Variable], axis: Axis):
    s1 = v_pair[0].shape_dict[axis]
    im = op.inputs["im"]
    cols = [op.outputs[f"col{i}"] for i in range(len(op.outputs))]
    sections = op.sections

    if v == im:
        raise NotImplementedError(f"Variable is too large to handle in WebGL backend: {v}")

    elif v in cols:
        op.remove_all()

        if axis == op.axis:
            """
            before)
                                +- col0
                                |
            im -{PartialIm2Col}-+- col1
                                |
                                +- col2

            after)
                                +- col0
                                |
                                +- col1_0
            im -{PartialIm2Col}-+
                                +- col1_1
                                |
                                +- col2
            """
            target_i = cols.index(v)

            s_insert = (0 if target_i == 0 else sections[target_i - 1]) + s1
            new_sections = list(sections)
            new_sections.insert(target_i, s_insert)

            cols.pop(target_i)
            cols.insert(target_i + 0, v_pair[0])
            cols.insert(target_i + 1, v_pair[1])

            new_cols = PartialIm2Col(None,
                                     ksize=op.ksize, stride=op.stride, padding=op.padding, dilation_rate=op.dilation_rate,
                                     axis=axis, sections=new_sections)(im)
            for col, new_col in zip(cols, new_cols):
                OptimizeRule.replace_variable(graph, new_col, col)

        else:
            raise NotImplementedError(f"Variable is too large to handle in WebGL backend: {v}")

    else:
        raise UnexpectedAndPleaseReportError


def _split_tensordot(graph: Graph, op: Tensordot, v: Variable, v_pair: Sequence[Variable], axis: Axis):
    s1 = v_pair[0].shape_dict[axis]
    s2 = v_pair[1].shape_dict[axis]
    A = op.inputs["A"]
    B = op.inputs["B"]
    C = op.outputs["C"]
    axes_M = tuple(filter(lambda a: a not in op.axes[0], A.order.axes))
    axes_N = tuple(filter(lambda a: a not in op.axes[1], B.order.axes))

    axes_K_A, axes_K_B = op.axes

    K = mul(A.shape_dict[a] for a in axes_K_A)
    M = A.size // K
    N = B.size // K

    shape_M = [A.shape_dict[a] for a in axes_M]
    shape_N = [B.shape_dict[a] for a in axes_N]

    op.remove_all()

    if v == A:
        A1, A2 = v_pair

        if axis in axes_K_A:
            split_axis_A = axis

            if (B.shape_dict[axes_K_B[0]] * s1) % (s1 + s2) == 0:
                split_axis_B = axes_K_B[0]

            else:
                # Factorize B's axes consisting to K into A's corresponding axes
                B = B.transpose(Order(axes_N + axes_K_B))
                B = B.reshape(order=Order((Axis(),) + axes_K_A), shape=[N] + [A.shape_dict[a] for a in axes_K_A])
                split_axis_B = split_axis_A
                axes_K_B = axes_K_A

            B1, B2 = SplitAxis(None, axis=split_axis_B, sections=[(B.shape_dict[split_axis_B] * s1) // (s1 + s2)])(B)

            C1, = Tensordot(None, [axes_K_A, axes_K_B])(A1, B1)
            C2, = Tensordot(None, [axes_K_A, axes_K_B])(A2, B2)
            OptimizeRule.replace_variable(graph, (C1 + C2).reshape(shape_M + shape_N, Order(axes_M + axes_N)).transpose_like(C), C)

        else:
            C1, = Tensordot(None, op.axes)(A1, B)
            C2, = Tensordot(None, op.axes)(A2, B)

            for a1, a2 in zip(C1.order.axes, C2.order.axes):
                if a1 == a2 == axis:
                    continue
                a1.unify(a2)

            C_new, = Concat(None, axis=axis)(C1, C2)
            OptimizeRule.replace_variable(graph, C_new, C)

    elif v == B:
        B1, B2 = v_pair

        if axis in axes_K_B:
            split_axis_B = axis

            if (A.shape_dict[axes_K_A[0]] * (s1 + s2)) % s1 == 0:
                split_axis_A = axes_K_A[0]

            else:
                # Factorize A's axes consisting to K into B's corresponding axes
                A = A.transpose(Order(axes_M + axes_K_A))
                A = A.reshape(order=Order((Axis(),) + axes_K_B), shape=[M] + [B.shape_dict[a] for a in axes_K_B])
                split_axis_A = split_axis_B
                axes_K_A = axes_K_B

            A1, A2 = SplitAxis(None, axis=split_axis_A, sections=[(A.shape_dict[split_axis_A] * s1) // (s1 + s2)])(A)

            C1, = Tensordot(None, [axes_K_A, axes_K_B])(A1, B1)
            C2, = Tensordot(None, [axes_K_A, axes_K_B])(A2, B2)
            OptimizeRule.replace_variable(graph, (C1 + C2).reshape(shape_M + shape_N, Order(axes_M + axes_N)).transpose_like(C), C)

        else:
            C1, = Tensordot(None, op.axes)(A, B1)
            C2, = Tensordot(None, op.axes)(A, B2)

            for a1, a2 in zip(C1.order.axes, C2.order.axes):
                if a1 == a2 == axis:
                    continue
                a1.unify(a2)

            C_new, = Concat(None, axis=axis)(C1, C2)
            OptimizeRule.replace_variable(graph, C_new, C)

    elif v == C:
        """
        before)

            C[M, N] = A[M, K] @ B[K, N]

        after) In case `axis` is in `N`,

            C[M, N1] = Concat(A[M, K] @ B1[K, N1])
            C[M, N2] = Concat(A[M, K] @ B2[K, N2])
        """
        raise NotImplementedError(f"Variable is too large to handle in WebGL backend: {v}")

    else:
        raise UnexpectedAndPleaseReportError


def _split_pooling_2d(graph: Graph, op: Pooling2D, v: Variable, v_pair: Sequence[Variable], axis: Axis):
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


def _split_tensorwise(graph: Graph, op: Operator, v: Variable, v_pair: Sequence[Variable], axis: Axis):
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


def _listup_splittable_axis(v: Variable, op: Operator) -> List[Axis]:
    if isinstance(op, (Concat, SplitAxis)):
        return list(v.order.axes)

    if isinstance(op, Reshape):
        """
        For more detail of this condition check, please see the comment document of `_split_reshape`
        """
        splittable_axes = []  # type: List[Axis]
        v1 = v
        v2 = op.outputs["y"] if v == op.inputs["x"] else op.inputs["x"]
        v1_order = op.in_order if v1 == op.inputs["x"] else op.out_order
        v2_order = op.in_order if v2 == op.inputs["x"] else op.out_order
        v1_shape = [v1.shape_dict[a] for a in v1_order.axes]

        for a1 in v1_order.axes:
            d1 = mul(v1_shape[v1_order.axes_dict[a1]:])
            d2 = 1
            axes = []
            for a2 in reversed(v2_order.axes):
                d2 *= v2.shape_dict[a2]
                axes.append(a2)

                if d2 == d1 and any(v2.shape_dict[a3] % 2 == 0 for a3 in axes):  # TODO
                    splittable_axes.append(a1)
                    continue

                elif d2 > d1:
                    continue

        return splittable_axes

    if isinstance(op, Im2Col):
        op = op  # type: Im2Col
        if v in op.outputs.values():
            return [Axis.N, Axis.H, Axis.W, Axis.C]

        else:
            return []

    if isinstance(op, PartialIm2Col):
        op = op  # type: PartialIm2Col
        if v in op.outputs.values():
            axes = [Axis.N, Axis.C]
            if op.axis not in axes:
                axes.append(op.axis)

            return axes

        else:
            return []

    if isinstance(op, Tensordot):
        return list(v.order.axes)

    if isinstance(op, Pooling2D):
        return [Axis.H, Axis.W]

    return []


def _choose_split_axis(v: Variable) -> Axis:
    """
    For too-large texture `v`, choose one axis which is the best one to reduce texture size by splitting `v` in that axis.

    Args:
        v: Variable, whose size is too large (= this variable has :code:`SplitTarget` attribute)

    Returns:
        axis
    """

    ops = list(v.input_to)
    if v.output_from is not None:
        ops += [v.output_from]

    splittable_axes = list(v.order.axes)
    for op in ops:
        _op_splittable_axes = _listup_splittable_axis(v, op) + [attr.axis for attr in op.get_attribute(Tensorwise)]
        for a in list(splittable_axes):
            if a not in _op_splittable_axes:
                splittable_axes.remove(a)

    if len(splittable_axes) == 0:
        raise ValueError("No axis is splittable")

    # Calculate the size of a side of texture which will be changed when each axis is split
    #
    # ex) OrderNC, N=512, C=2048, texture(width=2048, height=512)
    #     => If axis `N` is split, then height will be changed => N: 512 (=height)
    #        If axis `C` is split, then width will be changed => C: 2048 (=width)
    #
    # ex) OrderNCHW, N=1, C=512, H=13, W=13, texture(width=2048, height=43)
    #     => TexW == W*H*(partial of C) texture width consists of axis W, H and C.
    #        TexH == (partial of C)*N   texture height consists of axis C and N.
    #     => N cannot be split => N: -1
    #        C is related both width and height. In this case, use large one. => C: 2048
    #        H is included in width =>  H: 2048
    #        W is also included in width =>  W: 2048

    axis_corresponding_texture_size = AxisKeyDict()
    element_per_pixel = ChannelMode.elements_per_pixel(v)
    tex_h, tex_w = TextureShape.get(v)
    tex_w = (tex_w + element_per_pixel - 1) // element_per_pixel
    for a in v.order.axes:
        if v.shape_dict[a] == 1:
            # This axis cannot be split
            axis_corresponding_texture_size[a] = -1

        elif v.stride_dict[a] >= tex_w * element_per_pixel:
            axis_corresponding_texture_size[a] = tex_h

        elif v.stride_dict[a] * v.shape_dict[a] >= tex_w * element_per_pixel:
            axis_corresponding_texture_size[a] = max(tex_h, tex_w)

        else:
            axis_corresponding_texture_size[a] = tex_w

    splittable_axes.sort(key=lambda a: axis_corresponding_texture_size[a], reverse=True)
    target_axis = splittable_axes[0]

    console.debug(f"===========================================================================")
    console.debug(f"{v}")
    console.debug(f"  original order: {v.order}")
    console.debug(f"  original shape: {v.shape}")
    console.debug(f"   texture shape: {TextureShape.get(v)}")
    console.debug(f"")
    console.debug(f"  splittable axis: {splittable_axes}")
    console.debug(f"  split axis: {target_axis}")
    console.debug(f"")
    console.debug(f"  related operators:")
    for related_op in ops:
        console.debug(f"---------------------------------------------------------------------------")
        traverse.dump_op(related_op)
    console.debug(f"")

    if axis_corresponding_texture_size[target_axis] <= 0:
        raise NotImplementedError(f"Variable is too large to handle in WebGL backend: {v}")

    return target_axis
