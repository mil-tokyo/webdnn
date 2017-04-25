from typing import Type, List, Set, Iterable, Union

from graph_builder.graph.attribute import Attribute
from graph_builder.graph.node import Node
from graph_builder.graph.operator import Operator
from graph_builder.graph.operators.compose import Compose, VariableAlias
from graph_builder.graph.variable import Variable

QueryTarget = Union[Type[Attribute], Type[Operator]]


def check_match(node: Node, query: QueryTarget):
    if issubclass(query, Attribute):
        return check_attribute_match(node, query)

    elif issubclass(query, Operator):
        return check_operator_match(node, query)

    else:
        raise NotImplementedError


def check_attribute_match(node: Node, query: Type[Attribute]):
    for attr in node.attributes:
        if issubclass(attr, query):
            return True

    else:
        return False


def check_operator_match(node: Node, query: Type[Operator]):
    return isinstance(node, query)


def search_sub_structure(graph: Operator, query: List[QueryTarget]) -> List[List[Operator]]:
    matches: List[List[Operator]] = []
    ops = listup_operator_in_order(graph)
    current_matches: List[(int, int)] = [(i, 0) for i, _ in enumerate(ops)]

    while len(current_matches) > 0:
        offset, index = current_matches.pop(0)
        if check_match(ops[offset + index], query[index]):
            if index == len(query) - 1:
                matches.append(ops[offset:offset + len(query)])

            else:
                current_matches.append((offset, index + 1))

    return matches


def filter_nodes(nodes: Iterable[Node], query: Type[Attribute]) -> List[Node]:
    return [node for node in nodes if check_attribute_match(node, query)]


def listup_operator_in_order(graph: Operator) -> List[Operator]:
    stack: List[Operator] = [graph]
    result: List[Operator] = []
    resolved: Set[Operator] = set()

    while len(stack) > 0:
        op = stack.pop(0)
        dependents: List[Operator] = []

        inputs = list(op.inputs.values())
        if isinstance(op, Compose):
            op: Compose
            inputs.extend(op.outputs_alias)

        for v in inputs:
            if v.output_from is not None and v.output_from not in resolved:
                dependents.append(v.output_from)

        if len(dependents) > 0:
            stack.insert(0, op)
            for dependent in dependents:
                stack.insert(0, dependent)

        else:
            result.append(op)
            resolved.add(op)

    return result


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
            op: Compose
            for var in op.outputs_alias:  # type: VariableAlias
                op_queue.append(var.output_from)

    return variables


def dump(graph: Operator):
    indent = ""
    for op in listup_operator_in_order(graph):
        print(f"---------------------------------------------------------------------------")
        print(f"{indent}{op.__class__.__name__} : {op.name}")
        print(f"{indent}    In  : {op.inputs}")
        print(f"{indent}    Out : {op.outputs}")
        print(f"{indent}    Attr: {[attr.__name__ for attr in op.attributes]}")
