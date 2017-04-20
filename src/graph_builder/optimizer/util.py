from typing import Type, List, Tuple, Set, Iterable

from graph_builder.graph import Attribute, Operator
from graph_builder.graph.graph import Node, Variable
from graph_builder.graph.operators import Compose
from graph_builder.graph.operators.compose import VariableAlias


def check_attribute_match(node: Node, query: Type[Attribute]):
    for attr in node.attributes:
        if issubclass(attr, query):
            return True

    else:
        return False


def search_sub_structure(root: Operator, query: List[Type[Attribute]], find_all: bool = False) -> List[List[Operator]]:
    queue: List[Tuple[List[Operator], Operator, int]] = [([], root, 0)]
    matches: List[List[Operator]] = []

    while len(queue) > 0:
        res, op, index = queue.pop()
        flag_match = check_attribute_match(op, query[index])
        if flag_match:
            res.append(op)

            if index == len(query) - 1:
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


def filter_nodes(nodes: Iterable[Node], query: Type[Attribute]) -> List[Node]:
    return [node for node in nodes if check_attribute_match(node, query)]


def listup_variables(op: Operator, remove_alias: True) -> Set[Variable]:
    op_queue: List[Operator] = [op]
    variables: Set[Variable] = set(op.outputs.values())
    checked_ops: Set[Operator] = set()

    while len(op_queue) > 0:
        op = op_queue.pop(0)
        if op in checked_ops:
            continue
        checked_ops.add(op)

        for var in op.inputs.values():
            if not remove_alias or not isinstance(var, VariableAlias):
                variables.add(var)

            if var.output_from is not None:
                op_queue.append(var.output_from)

        if isinstance(op, Compose):
            op = op  # type: Compose
            for var in op.outputs_alias:  # type: VariableAlias
                op_queue.append(var.output_from)

    return variables
