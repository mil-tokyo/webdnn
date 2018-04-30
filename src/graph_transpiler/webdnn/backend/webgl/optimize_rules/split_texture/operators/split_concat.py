from typing import NamedTuple, List, Sequence

from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.operators.concat import Concat
from webdnn.graph.operators.split_axis import SplitAxis
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.variable import Variable
from webdnn.util.assertion import UnexpectedAndPleaseReportError


class GraphVars(NamedTuple):
    inputs: List[Variable]
    hidden: List[Variable]
    outputs: List[Variable]


def split_concat(graph: Graph, op: Concat, v: Variable, v_pair: Sequence[Variable], axis: Axis):
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
