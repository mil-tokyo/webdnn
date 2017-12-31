from typing import List, Tuple

from webdnn.graph.graph import Graph
from webdnn.graph.operator import Operator
from webdnn.graph.variable import Variable


class OptimizeRule:
    @staticmethod
    def replace_input(graph: Graph, op: Operator, old_var: Variable, new_var: Variable, with_assert: bool = True): ...

    @staticmethod
    def replace_output(graph: Graph, op: Operator, old_var: Variable, new_var: Variable, with_assert: bool = True): ...

    @staticmethod
    def replace_variable(graph: Graph, old_var: Variable, new_var: Variable, with_assert: bool = True): ...

    def flags(self) -> List[bool]: ...

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]: ...


class OptimizeRuleGroup(OptimizeRule):
    repeat: bool
    sub_rules: List[OptimizeRule]

    def __init__(self, rules: List[OptimizeRule], repeat: bool = True): ...

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]: ...

    def append_sub_rule(self, rule: OptimizeRule): ...
