from typing import List, Tuple

from graph_builder.graph.operator import Operator
from graph_builder.optimizer import util
from graph_builder.optimizer.optimize_rule import OptimizeRule
from graph_builder.util import flags


class Optimizer(OptimizeRule):
    rules: List[OptimizeRule]

    def __init__(self):
        self.rules = []

    def optimize(self, graph: Operator) -> Operator:
        return self(graph)[0]

    def __call__(self, graph: Operator) -> Tuple[Operator, bool]:

        flag_retry = True
        flag_totally_changed = False

        while flag_retry:
            flag_retry = False

            for rule in self.rules:
                graph, flag_changed = rule(graph)
                flag_retry |= flag_changed

                if flags.DEBUG:
                    print(f"[Optimizer] optimize rule={rule} changed={flag_changed}")
                    util.dump(graph)
                    print()

            flag_totally_changed |= flag_retry

        return graph, flag_totally_changed

    def register(self, rule: OptimizeRule):
        self.rules.append(rule)
