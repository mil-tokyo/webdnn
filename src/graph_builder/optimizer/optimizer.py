from typing import List

from graph_builder.graph.graph import Operator
from graph_builder.optimizer.optimize_rule import OptimizeRule


class Optimizer:
    rules: List[OptimizeRule]

    def __init__(self):
        self.rules = []

    def optimize(self, graph: Operator):

        flag_retry = True
        while flag_retry:
            flag_retry = False
            for rule in self.rules:
                graph, flag_changed = rule(graph)
                flag_retry |= flag_changed

        return graph

    def register_rule(self, rule: OptimizeRule):
        self.rules.append(rule)
