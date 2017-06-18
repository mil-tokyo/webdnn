from typing import Type, List, Set, Iterable, Union, Tuple

from webdnn.graph.attribute import Attribute
from webdnn.graph.graph import Graph
from webdnn.graph.node import Node
from webdnn.graph.operator import Operator
from webdnn.graph.variable import Variable
from webdnn.util import console

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
        if isinstance(attr, query):
            return True

    else:
        return False


def check_node_type_match(node: Node, query: Type[Node]):
    return isinstance(node, query)


def search_sub_structure(graph: Graph, query: List[Query]) -> List[List[Operator]]:
    matches: List[List[Operator]] = []
    queue: List[Tuple(Node, int, List[Node])] = [(node, 0, []) for node in listup_nodes(graph)]

    while len(queue) > 0:
        node, index, matched = queue.pop(0)
        if check_match(node, query[index]):
            matched.append(node)

            if index == len(query) - 1:
                matches.append(matched)

            else:
                for next in node.nexts:
                    queue.append((next, index + 1, list(matched)))

    return matches


def filter_nodes(nodes: Iterable[Node], query: Query, mode_not: bool = False) -> List[Node]:
    return [node for node in nodes if not mode_not == check_match(node, query)]


def listup_nodes(graph: Graph) -> List[Node]:
    stack: List[Node] = list(graph.outputs)
    result: List[Node] = []
    resolved: Set[Node] = set()

    while len(stack) > 0:
        node = stack.pop(0)
        if node in resolved:
            continue

        unresolved = [d for d in node.prevs if (d is not None) and (d not in resolved)]

        if len(unresolved) > 0:
            stack.insert(0, node)
            for dependent in unresolved:
                stack.insert(0, dependent)

        else:
            result.append(node)
            resolved.add(node)

    return result


def listup_operators(graph: Graph) -> List[Operator]:
    ops: List[Operator] = filter_nodes(listup_nodes(graph), Operator)
    return ops


def listup_variables(graph: Graph) -> List[Variable]:
    variables: List[Variable] = filter_nodes(listup_nodes(graph), Variable)
    return variables


def dump(graph: Graph):
    indent = ""
    for op in listup_operators(graph):
        console.debug(f"---------------------------------------------------------------------------")
        console.debug(f"{indent}{op.__class__.__name__} : {op.name}")
        console.debug(f"{indent}    In  : {op.inputs}")
        console.debug(f"{indent}    Out : {op.outputs}")
        console.debug(f"{indent}    Attr: {[attr.__class__.__name__ for attr in op.attributes]}")
