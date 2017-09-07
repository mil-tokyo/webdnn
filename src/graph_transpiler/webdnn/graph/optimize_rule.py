from typing import List, Tuple

from webdnn.graph.graph import Graph
from webdnn.graph.variable import Variable
from webdnn.util import console


class OptimizeRule:
    """OptimizeRule()

    :code:`OptimizeRule` transforms IR graph. This class used not only for just optimization, but also analysis, fallback supports, and so on.

    When :func:`optimize(graph)<OptimizeRule.optimize>` is called, the transform rule is applied for given graph. In the single call,
    the rule is applied multiple times until the graph will be not changed.
    """

    def __init__(self):
        self.sub_rules = []  # type:List["OptimizeRule"]

    @staticmethod
    def replace_variable(graph: Graph, old_var: Variable, new_var: Variable):
        old_var.replace(new_var)

        if old_var in graph.inputs:
            i = graph.inputs.index(old_var)
            graph.inputs.remove(old_var)
            graph.inputs.insert(i, new_var)

        if old_var in graph.outputs:
            i = graph.outputs.index(old_var)
            graph.outputs.remove(old_var)
            graph.outputs.insert(i, new_var)

    def flags(self):
        """optimize(graph)

        Return list of boolean values. If False is contained more than zero, this optimize rule is not applied.
        returns:
            (tuple of bool): boolean values
        """
        return []

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        """optimize(graph)

        Optimize the given graph. In the single call, this rule is applied multiple times until the graph will be not changed.

        args:
            graph(:class:`~webdnn.Graph`): Computational graph

        returns:
            (tuple of :class:`~webdnn.Graph` and bool): Optimized graph and flag whether the graph is changed or not.
        """
        if not all(self.flags()):
            return graph, False

        flag_retry = True
        flag_totally_changed = False

        while flag_retry:
            flag_retry = False

            for sub_rule in self.sub_rules:
                if not all(sub_rule.flags()):
                    continue

                graph, flag_changed = sub_rule.optimize(graph)
                if flag_changed:
                    console.debug(f"[OptimizeRule] apply: {sub_rule.__class__.__name__}")

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
