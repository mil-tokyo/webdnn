from typing import List, Tuple

from webdnn.graph.graph import Graph


class OptimizeRule:
    """OptimizeRule()

    :code:`OptimizeRule` transforms IR graph. This class used not only for just optimization, but also analysis, fallback supports, and so on.

    When :func:`optimize(graph)<OptimizeRule.optimize>` is called, the transform rule is applied for given graph. In the single call,
    the rule is applied multiple times until the graph will be not changed.
    """

    def __init__(self):
        self.sub_rules = []  # type:List["OptimizeRule"]

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        """optimize(graph)

        Optimize the given graph. In the single call, this rule is applied multiple times until the graph will be not changed.

        args:
            graph(:class:`~webdnn.Graph`): Computational graph

        returns:
            (tuple of :class:`~webdnn.Graph` and bool): Optimized graph and flag whether the graph is changed or not.
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
        """register(rule)

        Register new sub rule. Registered sub rules are applied when this rule is applied.

        args:
            rule(:class:`~webdnn.OptimizeRule`): new sub rule
        """
        self.sub_rules.append(rule)
