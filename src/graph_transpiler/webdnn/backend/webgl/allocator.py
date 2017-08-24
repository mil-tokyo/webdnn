from typing import Dict, List, Set, Tuple

from webdnn.backend.webgl.attributes.channel_mode import ChannelModeEnum, ChannelMode
from webdnn.graph import traverse
from webdnn.graph.graph import Graph
from webdnn.graph.operator import Operator
from webdnn.graph.operators.attributes.inplace import Inplace
from webdnn.graph.placeholder import Placeholder
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable
from webdnn.util import flags, console


class Allocation:
    """
    Allocation information with variable's lifetime

    ex)

       t = 0         |   t = 1    |   t = 2
    ==============================================
                     |            |
        +-{op1}- v2 -|-{op2}- v3 -|-+
    v1 -+            |            | +-{op3}-> v4
        +------------|------------|-+
                     |            |

    In this case,

        lifetimes = {
            v1: { begin: 0, end: 3 },
            v2: { begin: 0, end: 2 },
            v3: { begin: 1, end: 3 },
            v4: { begin: 2, end: 3 },
        }

    Note that when t=end, the variable is not exist (the variable is exist in `[begin, end)`).
    """

    _uuid = 0

    def __init__(self, size: int, begin: int, end: int, channel_mode: ChannelModeEnum):
        Allocation._uuid += 1
        self.name = f"a{str(Allocation._uuid)}"
        self.size = size
        self.begin = begin
        self.end = end
        self.channel_mode = channel_mode


def allocate(graph: Graph) -> Dict[Variable, Allocation]:
    nodes = traverse.listup_nodes(graph)
    operators = traverse.filter_nodes(nodes, Operator)  # type: List[Operator]
    variables = traverse.filter_nodes(nodes, Variable)  # type: List[Variable]

    for i, v in enumerate(variables):
        if v.name is None:
            v.name = f"v{i}"

    # check if constant variable has unresolved shape.
    dynamic_constants = traverse.filter_nodes([v for v in variables if not Placeholder.check_resolved(v.size)], ConstantVariable)
    assert len(dynamic_constants) == 0, f"ConstantVariable with unresolved placeholder shape is detected: f{dynamic_constants}"

    allocations = _get_allocations(graph, operators, variables)
    # _optimize_buffer_reuse(allocations)

    return allocations


def _get_allocations(graph: Graph, operators: List[Operator], variables: List[Variable]) -> Dict[Variable, Allocation]:
    T_UNKNOWN = -1
    T_LAST = len(operators)

    allocations = {}  # type: Dict[Variable, Allocation]
    retain_count = {v: 0 for v in variables}  # type: Dict[Variable, int]
    allocated = set()  # type: Set[Variable]

    for v in traverse.filter_nodes(variables, ConstantVariable):  # type: ConstantVariable
        # Constant variable cannot be released
        allocations[v] = Allocation(size=v.size, begin=0, end=T_LAST, channel_mode=v.get_attribute(ChannelMode)[0].mode)
        allocated.add(v)

    for v in graph.inputs:
        # Input variable cannot be released
        allocations[v] = Allocation(size=v.size, begin=0, end=T_LAST, channel_mode=v.get_attribute(ChannelMode)[0].mode)
        allocated.add(v)

    for v in graph.outputs:
        # Output variable cannot be released, but it's not needed to be allocated from the begin
        allocations[v] = Allocation(size=v.size, begin=T_UNKNOWN, end=T_LAST, channel_mode=v.get_attribute(ChannelMode)[0].mode)
        allocated.add(v)

    for t, op in enumerate(operators):
        # Allocate output variables
        for v in op.outputs.values():
            if v in allocated:
                if allocations[v].begin == T_UNKNOWN:
                    allocations[v].begin = t

            else:
                allocations[v] = Allocation(size=v.size, begin=t, end=T_UNKNOWN, channel_mode=v.get_attribute(ChannelMode)[0].mode)
                retain_count[v] = len(v.input_to)
                allocated.add(v)

        # Release input variables if needed
        for v in op.inputs.values():
            if v not in allocated:
                # Allocate
                allocations[v] = Allocation(size=v.size, begin=t, end=T_UNKNOWN, channel_mode=v.get_attribute(ChannelMode)[0].mode)
                retain_count[v] = len(v.input_to)
                allocated.add(v)

            if allocations[v].end != T_UNKNOWN:
                # Release time is already determined (input, output, or constant variable).
                continue

            retain_count[v] -= 1
            if retain_count[v] == 0:
                # `t + 1` means that `v` will be released *AFTER* `op` will be finished.
                allocations[v].end = t + 1

    return allocations


def _optimize_buffer_reuse(allocations_dict: Dict[Variable, Allocation]):
    """
    Optimize memory size by reusing buffer if available

    Algorithm:

    Considering 4 variables with follow size and lifetime.

    Size and Lifetime)

      var |size| Lifetime (t=0 -> ...)
      ----+----+-----------------------
        a | 10 | |-|
        b |  9 |     |-|
        c |  1 |      |-|
        d |  3 |           |-|

    Construct a graph whose edges mean two variables can be merged

    Graph)

      +-----[ 9 ]-----c
      |               |
      a-[ 3 ]-d-[ 3 ]-+
      |       |
      |     [ 1 ]
      |       |
      +-[ 1 ]-b

    Each edge weight is smaller one of memory size of two nodes (= The memory size which is reduced if two nodes are merged).

    Edge a-c has the larges weight, so variable a and c is merged
    - d has edges with both a and c, so these edges are kept after a and c are merged.
    - b has the edge with only a, so the edge is removed after a and c are merged.

    Size and Lifetime)

      var |size| Lifetime (t=0 -> ...)
      ----+----+-----------------------
       ac | 10 | |-|  |-|
        b |  1 |     |-|
        d |  3 |           |-|

    Graph)

      ac-[ 3 ]-d
               |
             [ 1 ]
               |
               b

    Iterate.

    Edge ac-d has the larges weight, so variable ac and d is merged
    - b has the edge with only d, so the edge is removed after ac and d are merged.

    Size and Lifetime)

      var |size| Lifetime (t=0 -> ...)
      ----+----+-----------------------
      acd | 10 | |-|  |-|  |-|
        b |  1 |     |-|

    Graph)

      acd b

    There are no edge, so it's finished.
    """

    if not flags.optimize.OPTIMIZE:
        console.debug('_optimize_buffer_reuse is skipped')
        return

    allocations = list(set(filter(lambda x: Placeholder.check_resolved(x), allocations_dict.values())))
    N = len(allocations)

    # List of `(cost, i1, i2)`
    cost = []  # type: List[Tuple[int, int, int]]
    connection_matrix = [[False for _ in allocations] for _ in allocations]

    readonly_allocations = [a for v, a in allocations_dict.items() if isinstance(v, ConstantVariable)]
    for i1, a1 in enumerate(allocations):
        if a1 in readonly_allocations:
            continue

        for i2, a2 in enumerate(allocations[i1 + 1:]):
            if a2 in readonly_allocations:
                continue

            if a1.channel_mode == a2.channel_mode and (a1.end <= a2.begin or a2.end <= a1.begin):
                connection_matrix[i1][i2] = True
                connection_matrix[i2][i1] = True
                cost.append((min(a1.size, a2.size), i1, i2))

    cost = sorted(cost, key=lambda x: x[0], reverse=True)
    tree = [[] for _ in allocations]
    while len(cost) > 0:
        _, i1, i2 = cost.pop()
        if not connection_matrix[i1][i2]:
            continue

        # merge i1 and i2
        tree[i1].append(i2)
        connection_matrix[i1][i2] = False
        connection_matrix[i2][i1] = False

        # update connection matrix
        for i3 in range(0, N):
            if connection_matrix[i1][i3] and not connection_matrix[i2][i3]:
                connection_matrix[i1][i3] = False
                connection_matrix[i3][i1] = False

            elif not connection_matrix[i1][i3] and connection_matrix[i2][i3]:
                connection_matrix[i2][i3] = False
                connection_matrix[i3][i2] = False

    # update allocation dict
    new_allocations = list(allocations)
    for i1, i2s in enumerate(tree):
        allocation1 = new_allocations[i1]

        for i2 in i2s:
            allocation2 = new_allocations[i2]
            allocation1.size = max(allocation1.size, allocation2.size)
            allocation1.begin = min(allocation1.begin, allocation2.begin)
            allocation1.end = max(allocation1.end, allocation2.end)
            new_allocations[i2] = allocation1

    allocation_mapping = dict(zip(allocations, new_allocations))
    for variable, allocation in allocations_dict.items():
        allocations_dict[variable] = allocation_mapping[allocation]


def _merge_allocation(allocations: Dict[Variable, Allocation], a1: Allocation, a2: Allocation, a_new: Allocation):
    """
    merge two allocations into one new allocation 
    """
    for v, lifetime in allocations.items():
        if lifetime == a1 or lifetime == a2:
            allocations[v] = a_new
