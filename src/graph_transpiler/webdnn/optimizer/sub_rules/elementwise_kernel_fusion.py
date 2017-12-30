from typing import Tuple, List

from webdnn.graph import traverse
from webdnn.graph.graph import Graph
from webdnn.graph.operators.elementwise import Elementwise
from webdnn.graph.operators.fused_elementwise import FusedElementwise
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.util import flags


def _find_elementwise_sub_graph(graph: Graph) -> List[Graph]:
    """
    Find all sub graphs which are consisted of only elementwise operators

    For each sub graph, follow conditions are checked about all input variable :code:`x`.

        - :code:`x.output_from` is elementwise operator.
        - All operators in :code`x.input_to` are included in sub graph

    And if satisfied, `x.output_from` is merged into sub graph. If `x.output_from` is already merged into other sub graph, then two sub
    graph are merged into single sub graph.

    In follow examples, let all operators be elementwise.

    ex.1)

    ...code-block:: text

                                  sub_graph                              sub_graph
                                  +-------+                        +-------------------+
                     +-{op1}-> v1-|-{op3}-|-> v3                 +-|-{op1}-> v1 -{op3}-|-> v3
                     |            +-------+                      | +-------------------+
        -{op0}-> v0 -+                           => -{op0}-> v0 -+
                     |                                           |
                     +-{op2}-> v2                                +-{op2}-> v2

    Considering :code:`v1`,
        - :code:`v1.output_from = op1` is elementwise operator.
        - :code:`v1.input_to` contains only :code:`op3`, which is included in sub graph.

    Therefore :code:`op1` is merged into sub graph, and :code:`v0` is registered as input variable.

    Considering :code:`v0`,
        - :code:`v0.output_from = op0` is elementwise operator.
        - :code:`v0.input_to` is :code:`op1` and :code:`op2`, and op2 is not included in sub graph

    Therefore :code:`op0` cannot be merged into sub graph.

    ex.2)

    ...code-block:: text

                                                                 +---------------------+
        -{op0}-> v0 -{op1}-> v1 -+                 -{op0}-> v0 --|-{op1}-> v1 -+       |
                                 | +-------+                     |             |       |
                                 +-|-{op3}-|-v3 =>             +-|-------------+-{op3}-|-> v3
                                 | +-------+                   | +---------------------+
                                 |                             |
                    -{op2}-> v2 -+                 -{op2}-> v2-+

    Considering :code:`v1`,
        - :code:`v1.output_from = op1` is elementwise operator.
        - :code:`v1.input_to` is only :code:`op3`, which is included in sub graph.

    Therefore :code:`op1` is merged into sub graph, and :code:`v0` is registered as input variable.

    ex.3)

    ...code-block:: text

                                                      +-----------------------------------+
                     +-{op1}-> v1 -+                  |             +-{op1}-> v1 -+       |
                     |             | +-------+        |             |             |       |
        -{op0}-> v0 -+             +-|-{op3}-|-v3 => -|-{op0}-> v0 -+             +-{op3}-|-> v3
                     |             | +-------+        |             |             |       |
                     +-{op2}-> v2 -+                  |             +-{op2}-> v2 -+       |
                                                      +-----------------------------------+

    Considering :code:`v1`,
        - :code:`v1.output_from = op1` is elementwise operator.
        - :code:`v1.input_to` contains only :code:`op3`, which is included in sub graph.

    Therefore :code:`op1` is merged into sub graph, and :code:`v0` is registered as input variable.

    Considering :code:`v2`,
        - :code:`v2.output_from = op2` is elementwise operator.
        - :code:`v2.input_to` contains only :code:`op3`, which is included in sub graph.

    Therefore :code:`op2` is  also merged into sub graph.

    Considering :code:`v0`,
        - :code:`v0.output_from = op0` is elementwise operator.
        - :code:`v0.input_to` is :code:`op1` and :code`op2`, both are included in sub graph.

    Therefore :code:`op0` is also merged into sub graph.

    Returns:
        (list of :class:`~webdnn.graph.graph.Graph`): list of sub graphs
    """
    queue = list(traverse.filter_nodes(traverse.listup_operators(graph), Elementwise))
    sub_graphs = {op: Graph(list(op.inputs.values()), list(op.outputs.values())) for op in queue}
    result = []

    while len(queue) > 0:
        out_node = queue.pop()
        sub_graph = sub_graphs[out_node]

        flag_changed = False
        new_inputs = []
        for x in sub_graph.inputs:
            # Condition 1: x.output_from is elementwise operator
            if not isinstance(x.output_from, Elementwise):
                new_inputs.append(x)
                continue

            # Condition 2: All operators in x.input_to are included in sub graph
            if not _check_condition2(x, sub_graph):
                new_inputs.append(x)
                continue

            # Sub graph can be merged with x.output_from
            if x.output_from in queue:
                new_inputs.extend(sub_graphs[x.output_from].inputs)
                queue.remove(x.output_from)
                flag_changed = True

            elif x.output_from in result:
                result.remove(x.output_from)
                new_inputs.extend(sub_graphs[x.output_from].inputs)
                flag_changed = True

            else:
                new_inputs.extend(sub_graphs[x.output_from].inputs)
                flag_changed = True

        sub_graph.inputs = list(set(new_inputs))

        if flag_changed:
            queue.append(out_node)

        else:
            result.append(out_node)

    return list(filter(lambda g: len(traverse.listup_operators(g)) >= 2, [sub_graphs[op] for op in result]))


def _check_condition2(v, sub_graph):
    ops = traverse.listup_operators(sub_graph)

    for op in v.input_to:
        if op not in ops:
            return False

    return True


class ElementwiseKernelFusion(OptimizeRule):
    def flags(self):
        return [
            flags.optimize.OPTIMIZE,
            flags.optimize.ELEMENTWISE_KERNEL_FUSION
        ]

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        sub_graphs = _find_elementwise_sub_graph(graph)

        if len(sub_graphs) == 0:
            return graph, False

        for sub_graph in sub_graphs:
            FusedElementwise(None, sub_graph)

        return graph, True
