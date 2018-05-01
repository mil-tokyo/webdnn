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


def split_splitaxis(graph: Graph, op: SplitAxis, v: Variable, v_pair: Sequence[Variable], axis: Axis):
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
                    yn_1 = Variable([y.shape_dict[axis] - (s1 - total_size) if a == axis else y.shape_dict[a] for a in
                                     y.order.axes],
                                    y.order)
                    OptimizeRule.replace_variable(graph, Concat(None, axis=axis)(yn_0, yn_1)[0].change_order(y.order),
                                                  y)
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
