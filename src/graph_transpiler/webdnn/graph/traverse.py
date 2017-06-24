from typing import Type, List, Set, Iterable, Union, Tuple, Optional

from webdnn.graph.attribute import Attribute
from webdnn.graph.graph import Graph
from webdnn.graph.node import Node
from webdnn.graph.operator import Operator
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable
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
    ops = filter_nodes(listup_nodes(graph), Operator)  # type: List[Operator]
    return ops


def listup_variables(graph: Graph) -> List[Variable]:
    variables = filter_nodes(listup_nodes(graph), Variable)  # type: List[Variable]
    return variables


def dump(graph: Graph):
    indent = ""
    for op in listup_operators(graph):
        console.debug(f"---------------------------------------------------------------------------")
        console.debug(f"{indent}{op.__class__.__name__} : {op.name}")
        console.debug(f"{indent}    In  : {op.inputs}")
        console.debug(f"{indent}    Out : {op.outputs}")
        console.debug(f"{indent}    Attr: {[attr.__class__.__name__ for attr in op.attributes]}")


def dump_dot(graph: Graph, name: Optional[str]=None) -> str:
    """
    Dumps graph into dot language for visualization.

    Args:
        graph: Target graph

    Returns:
        source code of dot language.
    """
    dot_source = ""
    dot_source += "digraph webdnn_ir {\n"

    # graph setting
    dot_source += "graph [\n"
    if name:
        dot_source += f"label=\"{name}\"\n"
    dot_source += "];\n"

    added_variables = set()

    def visualize_variable(var: Variable) -> str:
        if var in added_variables:
            return ""
        node_attrs = {}
        node_attrs["label"] = f"\"{var.name}\n{var.shape}\nOrder={var.order}\""
        if isinstance(var, ConstantVariable):
            node_attrs["shape"]="doubleoctagon"
        else:
            node_attrs["shape"]="octagon"
        if var in graph.inputs:
            node_attrs["style"]="\"dashed\""
        if var in graph.outputs:
            node_attrs["style"]="\"bold\""

        dot_source_var = ""
        dot_source_var += f"var_{id(var)} [\n"
        dot_source_var += ",".join(f"{attr_key}={attr_value}" for attr_key, attr_value in node_attrs.items())
        dot_source_var += "];\n"
        added_variables.add(var)
        return dot_source_var

    for op in listup_operators(graph):
        op_params = getattr(op, "parameters", {})
        op_params_str = "\n".join(f"{k}={v}" for k, v in op_params.items())
        dot_source += f"op_{op.name} [label=\"{op.name}\n{op.__class__.__name__}\n{op_params_str}\", shape=box];\n"
        for connection_name, var in op.inputs.items():
            dot_source += visualize_variable(var)
            dot_source += f"var_{id(var)} -> op_{op.name} [label=\"{connection_name}\"];\n"
        for connection_name, var in op.outputs.items():
            dot_source += visualize_variable(var)
            dot_source += f"op_{op.name} -> var_{id(var)} [label=\"{connection_name}\"];\n"
    dot_source += "}"
    return dot_source
