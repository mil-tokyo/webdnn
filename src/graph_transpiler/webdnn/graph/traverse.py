from typing import Type, List, Set, Iterable, Union, Tuple, Optional, TypeVar

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


T = TypeVar("T", bound=Node)


def filter_nodes(nodes: Iterable[T], query: Query, mode_not: bool = False) -> List[T]:
    return [node for node in nodes if not mode_not == check_match(node, query)]


def sort_nodes(nodes: List[Node]) -> List[Node]:
    return list(sorted(nodes, key=lambda x: x.name))


def listup_nodes(graph: Graph, ignore_internal_input_bound=False, ignore_internal_output_bound=True) -> List[Node]:
    """listup_nodes(graph, ignore_internal_input_bound, ignore_internal_output_bound)
    List up all nodes in graph in order of forward computation.

    `ignore_internal_` parameters control the result.

    .. code-block::

      # graph:
      #
      #   +-2-3-4-5-+
      # 1-+         +-6-
      #   +---------+

      listup_nodes(Graph([1, 3], [4, 6])

      # >>> ignore_internal_input_bound=False, ignore_internal_output_bound=False : [1,    3, 4,    6]
      # >>> ignore_internal_input_bound=False, ignore_internal_output_bound=True  : [1,    3, 4, 5, 6] (default)
      # >>> ignore_internal_input_bound=True,  ignore_internal_output_bound=False : [1, 2, 3, 4,    6]
      # >>> ignore_internal_input_bound=True,  ignore_internal_output_bound=True  : [1, 2, 3, 4, 5, 6]
    """

    input_bound = graph.inputs
    output_bound = graph.outputs

    # Normalize bound nodes

    def check_is_input_bound(node: Node):
        linked_nodes = list(node.prevs)  # type: List[Node]
        while len(linked_nodes) > 0:
            linked_node = linked_nodes.pop()

            if linked_node in graph.inputs:
                return False

            linked_nodes.extend(linked_node.prevs)

        return True

    def check_is_output_bound(node: Node):
        linked_nodes = list(node.nexts)  # type: List[Node]
        while len(linked_nodes) > 0:
            linked_node = linked_nodes.pop()

            if linked_node in graph.outputs:
                return False

            linked_nodes.extend(linked_node.nexts)

        return True

    if ignore_internal_input_bound and len(input_bound) >= 2:
        input_bound = list(filter(check_is_input_bound, input_bound))

    if ignore_internal_output_bound and len(output_bound) >= 2:
        output_bound = list(filter(check_is_output_bound, output_bound))

    # List up nodes

    stack = list(output_bound)  # type: List[Node]
    stacked = set(stack)  # type: Set[Node]
    resolved = set()  # type: Set[Node]
    result = list()  # type: List[Node]

    stack = sort_nodes(stack)

    for variable in input_bound:
        result.append(variable)
        resolved.add(variable)

    for variable in output_bound:
        resolved.update(variable.nexts)

    while len(stack) > 0:
        node = stack.pop()
        if node in resolved:
            continue

        unresolved_prev = [d for d in node.prevs if (d is not None) and (d not in resolved)]
        unstacked_next = [d for d in node.nexts if (d is not None) and (d not in stacked)]

        unresolved_prev = sort_nodes(unresolved_prev)
        unstacked_next = sort_nodes(unstacked_next)

        if len(unstacked_next) != 0:
            stack += unstacked_next
            stacked.update(unstacked_next)

        if len(unresolved_prev) == 0:
            resolved.add(node)
            result.append(node)

        else:
            stacked.update(unresolved_prev)
            stack.append(node)
            stack += unresolved_prev

    return result


def listup_operators(graph: Graph) -> List[Operator]:
    ops = filter_nodes(listup_nodes(graph), Operator)  # type: List[Operator]
    return ops


def listup_variables(graph: Graph) -> List[Variable]:
    variables = filter_nodes(listup_nodes(graph), Variable)  # type: List[Variable]
    return variables


def dump(graph: Graph):
    for op in listup_operators(graph):
        console.debug(f"---------------------------------------------------------------------------")
        dump_op(op)


def dump_op(op: Operator):
    parameters_sorted = [repr(key) + ': ' + str(op.parameters[key]) for key in sorted(op.parameters.keys())]
    console.debug(f"{op.__class__.__name__} : {op.name}")
    console.debug(f"    In  : {op.inputs}")
    console.debug(f"    Out : {op.outputs}")
    console.debug(f"    Attr: {', '.join(sorted(str(attr) for attr in op.attributes))}")
    console.debug(f"    Parameters: {{{', '.join(parameters_sorted)}}}")


def dump_dot(graph: Graph, name: Optional[str] = None) -> str:
    """
    Dumps graph into dot language for visualization.

    Args:
        graph: Target graph
        name:

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
        node_attrs["label"] = f"\"{var.name}\n{var.shape}\nOrder={var.order}"
        from webdnn.backend.webgl.attributes.texture_shape import TextureShape
        if var.has_attribute(TextureShape):
            node_attrs["label"] += f"\nTextureShape={TextureShape.get(var)}"
        from webdnn.backend.webgl.attributes.channel_mode import ChannelMode
        if var.has_attribute(ChannelMode):
            node_attrs["label"] += f"\nChannelMode={ChannelMode.get(var).name}"
        node_attrs["label"] += "\""
        if isinstance(var, ConstantVariable):
            node_attrs["shape"] = "doubleoctagon"
        else:
            node_attrs["shape"] = "octagon"
        if var in graph.inputs:
            node_attrs["style"] = "\"dashed\""
        if var in graph.outputs:
            node_attrs["style"] = "\"bold\""

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
