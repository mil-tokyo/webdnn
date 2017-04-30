from typing import Type, List, Set, Iterable, Union

from graph_builder.graph.attribute import Attribute
from graph_builder.graph.node import Node
from graph_builder.graph.operator import Operator
from graph_builder.graph.operators.compose import Compose, VariableAlias
from graph_builder.graph.variable import Variable

Query = Union[Type[Attribute], Type[Node]]


def check_match(node: Node, query: Query):
    if issubclass(query, Attribute):
        return check_attribute_match(node, query)

    elif issubclass(query, Node):
        return check_node_type_match(node, query)

    else:
        raise NotImplementedError


def check_attribute_match(node: Node, query: Type[Attribute]):
    for attr in node.attributes:
        if issubclass(attr, query):
            return True

    else:
        return False


def check_node_type_match(node: Node, query: Type[Node]):
    return isinstance(node, query)


def search_sub_structure(graph: Operator, query: List[Query]) -> List[List[Operator]]:
    matches: List[List[Operator]] = []
    ops = listup_operators(graph)
    current_matches: List[(int, int)] = [(i, 0) for i in range(len(ops) - len(query))]

    while len(current_matches) > 0:
        offset, index = current_matches.pop(0)
        if offset + index >= len(ops):
            continue

        if check_match(ops[offset + index], query[index]):
            if index == len(query) - 1:
                matches.append(ops[offset:offset + len(query)])

            else:
                current_matches.append((offset, index + 1))

    return matches


def filter_nodes(nodes: Iterable[Node], query: Query) -> List[Node]:
    return [node for node in nodes if check_match(node, query)]


def listup_nodes(graph: Operator) -> List[Node]:
    stack: List[Node] = list(graph.outputs.values())
    result: List[Node] = []
    resolved: Set[Node] = set()

    while len(stack) > 0:
        node = stack.pop(0)
        if node in resolved:
            continue

        if isinstance(node, Operator):
            if isinstance(node, Compose):
                node: Compose
                dependents = list([v.output_from for v in node.outputs_alias])

            else:
                dependents = list(node.inputs.values())

        elif isinstance(node, Variable):
            dependents = [node.output_from]

        elif isinstance(node, VariableAlias):
            dependents = [node.original]

        else:
            raise NotImplementedError("Unknown Node")

        unresolved = [d for d in dependents if (d is not None) and (d not in resolved)]

        if len(unresolved) > 0:
            stack.insert(0, node)
            for dependent in unresolved:
                stack.insert(0, dependent)

        else:
            if not isinstance(node, VariableAlias):
                result.append(node)
            resolved.add(node)

    return result


def listup_operators(graph: Operator) -> List[Operator]:
    ops: List[Operator] = filter_nodes(listup_nodes(graph), Operator)
    return ops


def listup_variables(graph: Operator) -> List[Variable]:
    variables: List[Variable] = filter_nodes(listup_nodes(graph), Variable)
    return variables


def dump(graph: Operator):
    indent = ""
    for op in listup_operators(graph):
        print(f"---------------------------------------------------------------------------")
        print(f"{indent}{op.__class__.__name__} : {op.name}")
        print(f"{indent}    In  : {op.inputs}")
        print(f"{indent}    Out : {op.outputs}")
        print(f"{indent}    Attr: {[attr.__name__ for attr in op.attributes]}")
