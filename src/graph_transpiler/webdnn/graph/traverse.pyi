from typing import Type, List, Iterable, TypeVar, overload
from typing import Union, Tuple, Optional, Sequence

from webdnn.graph.attribute import Attribute
from webdnn.graph.graph import Graph
from webdnn.graph.node import Node
from webdnn.graph.operator import Operator
from webdnn.graph.variable import Variable

# Query of traversing
Query = Union[Type[Attribute], Type[Node]]


def check_attribute_match(node: Node, attribute: Type[Attribute]) -> bool: ...


def check_node_type_match(node: Node, query: Type[Node]) -> bool: ...


def search_sub_structure(graph: Graph, queries: Sequence[Query]) -> List[Tuple[Node, ...]]: ...


T = TypeVar("T", bound=Node)
U = TypeVar("U", bound=Node)


@overload
def filter_nodes(nodes: Iterable[T], query: Type[Attribute], mode_not: bool = False) -> List[T]: ...


@overload
def filter_nodes(nodes: Iterable[T], query: Type[U], mode_not: bool = False) -> List[U]: ...


def sort_nodes(nodes: Iterable[Node]) -> Iterable[Node]: ...


def listup_nodes(graph: Graph, ignore_internal_input_bound=False, ignore_internal_output_bound=True) -> List[Node]: ...


def listup_operators(graph: Graph) -> List[Operator]: ...


def listup_variables(graph: Graph) -> List[Variable]: ...


def dump(graph: Graph): ...


def dump_op(op: Operator): ...


def dump_dot(graph: Graph, name: Optional[str] = None) -> str: ...
