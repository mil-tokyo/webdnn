from typing import List, Tuple

from webdnn.graph.graph import Graph


# FIXME: DOCS
class OptimizeRule:
    sub_rules: List["OptimizeRule"]

    def __init__(self):
        self.sub_rules = []

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        """Optimize the computational graph

        params:
            graph: Computational graph

        return:
            optimized graph and flag whether the graph is changed or not.
        """
        flag_retry = True
        flag_totally_changed = False

        while flag_retry:
            flag_retry = False

            for sub_rules in self.sub_rules:
                graph, flag_changed = sub_rules.optimize(graph)
                flag_retry |= flag_changed

            flag_totally_changed |= flag_retry

        return graph, flag_totally_changed

    def register(self, rule: "OptimizeRule"):
        self.sub_rules.append(rule)
