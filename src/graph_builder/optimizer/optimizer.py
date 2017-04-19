from typing import Set, Tuple, Iterable, List, Type

from graph_builder.graph.attribute import Attribute
from graph_builder.graph.graph import Operator
from graph_builder.optimizer.optimize_rule import OptimizeRule


class Optimizer:
    rules: Set[OptimizeRule]

    def optimize(self, graph: Operator):
        pass

    def register_rule(self, rule: OptimizeRule):
        # TODO: 最適化ルールの追加
        pass

    # noinspection PyMethodMayBeStatic
    def check_attribute_match(self, query: Type[Attribute], attributes: Iterable[Type[Attribute]]):
        for attr in attributes:
            if issubclass(attr, query):
                return True

        else:
            return False

    # noinspection PyMethodMayBeStatic
    def search_sub_structure(self, root: Operator, pattern: List[Type[Attribute]], find_all: bool = False) -> List[List[Operator]]:
        queue: List[Tuple[List[Operator], Operator, int]] = [([], root, 0)]
        matches: List[List[Operator]] = []

        while len(queue) > 0:
            res, op, index = queue.pop()
            flag_match = self.check_attribute_match(pattern[index], op.attributes)
            if flag_match:
                res.append(op)

                if index == len(pattern) - 1:
                    matches.append(res)
                    flag_match = False
                    if not find_all:
                        break

            for var in op.outputs.values():
                for next_op in var.input_to:
                    if flag_match:
                        queue.append((list(res), next_op, index + 1))

                    queue.append(([], next_op, 0))

        return matches
