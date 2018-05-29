from typing import Tuple

from webdnn.graph import traverse
from webdnn.graph.graph import Graph
from webdnn.graph.operators.concat import Concat
from webdnn.graph.optimize_rule import OptimizeRule


class UnrollConcat(OptimizeRule):
    """
    Concat kernel in WebGL backend can receive only 2 input variables.
    This optimization rule unroll concat operator into small concat operators

    before)

        x0 -+
            |
        x1 -+
            +-{concat}- y
        x2 -+
            |
        x3 -+

    after)

        x0 -+
            +-{concat}- h1 -+
        x1 -+               |
                            +-{concat}- y
        x2 -+               |
            +-{concat}- h2 -+
        x3 -+
    """

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        flag_changed = False
        for concat in traverse.filter_nodes(traverse.listup_operators(graph), Concat):
            if len(concat.inputs) == 2:
                # Unrolling is not needed
                continue

            flag_changed = True
            xs = [concat.inputs[f"x{i}"] for i in range(len(concat.inputs))]
            y = concat.outputs["y"]
            concat.remove_all()

            while len(xs) > 1:
                hs = []
                while len(xs) > 0:
                    if len(xs) == 1:
                        hs.append(xs.pop(0))

                    else:
                        x0, x1 = xs.pop(0), xs.pop(0)
                        h, = Concat(None, axis=concat.axis)(x0, x1)
                        hs.append(h)

                xs = hs

            OptimizeRule.replace_variable(graph, y, xs[0].transpose_like(y))

        return graph, flag_changed
