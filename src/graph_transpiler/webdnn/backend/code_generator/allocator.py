from enum import auto, Enum
from typing import Dict, List, Set, Union, Tuple, Sequence

import numpy as np

from webdnn.graph import traverse
from webdnn.graph.graph import Graph
from webdnn.graph.operator import Operator
from webdnn.graph.operators.attributes.inplace import Inplace
from webdnn.graph.placeholder import Placeholder
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable
from webdnn.util import json, flags, console

IntLike = Union[int, Placeholder]
AllocationDict = Dict[Variable, "Allocation"]
_T_UNKNOWN = -1

_count = 0


def _name(prefix: str):
    global _count
    _count += 1
    return f"{prefix}{_count}"


def _align(offset: int, unit: int = 1):
    return ((offset + unit - 1) // unit) * unit


_check_resolved = Placeholder.check_resolved


class BufferType(Enum):
    Static = auto()
    Dynamic = auto()


class Allocation(json.SerializableMixin):
    def __init__(self, size: IntLike, offset: IntLike = 0, begin: int = _T_UNKNOWN, end: int = _T_UNKNOWN, name: str = None):
        self.offset = offset
        self.size = size
        self.buffer_type = BufferType.Static if _check_resolved(offset) and _check_resolved(size) else BufferType.Dynamic
        self.begin = begin
        self.end = end
        self.name = _name('a') if name is None else name

    def _to_serializable_(self):
        return {
            "name": self.name,
            "offset": self.offset,
            "size": self.size
        }


class MemoryLayout(json.SerializableMixin):
    def __init__(self, allocations: AllocationDict = None, data: np.array = None):
        self.allocations = {} if allocations is None else allocations  # type: AllocationDict
        self.data = data  # type: np.array

    def _to_serializable_(self):
        return {
            "static": {
                "size": self.static_size,
                "allocations": {a.name: a for a in self.allocations.values() if a.buffer_type == BufferType.Static}
            },
            "dynamic": {
                "size": self.dynamic_size,
                "allocations": {a.name: a for a in self.allocations.values() if a.buffer_type == BufferType.Dynamic}
            }
        }

    def __len__(self):
        return len(self.allocations)

    def __getitem__(self, v: Variable):
        return self.allocations[v]

    def __contains__(self, v: Variable):
        return v in self.allocations

    @property
    def total_size(self) -> IntLike:
        return self.static_size + self.dynamic_size

    @property
    def static_size(self) -> int:
        size = 0
        for a in self.allocations.values():
            if a.buffer_type == BufferType.Static:
                size = max(a.offset + a.size, size)

        return size

    @property
    def dynamic_size(self) -> IntLike:
        size = 0
        for a in self.allocations.values():
            if a.buffer_type == BufferType.Dynamic:
                size += a.size

        return size


def allocate(graph: Graph) -> MemoryLayout:
    nodes = traverse.listup_nodes(graph)
    operators = traverse.filter_nodes(nodes, Operator)
    variables = traverse.filter_nodes(nodes, Variable)

    for i, v in enumerate(variables):
        if v.name is None:
            v.name = _name("v")

    dynamic_constants = traverse.filter_nodes([v for v in variables if not Placeholder.check_resolved(v.size)], ConstantVariable)
    assert len(dynamic_constants) == 0, f"ConstantVariable with unresolved placeholder shape is detected: f{dynamic_constants}"

    allocations = _get_allocations(graph, operators, variables)
    _optimize_inplace(operators, allocations)

    variable_allocations = {v: allocations[v] for v in variables if not isinstance(v, ConstantVariable)}
    constant_allocations = {v: allocations[v] for v in variables if isinstance(v, ConstantVariable)}

    _update_offset(variable_allocations)
    _optimize_buffer_reuse(variable_allocations)

    data = _update_constant_offset(constant_allocations)

    for allocation in set(variable_allocations.values()):
        if allocation.buffer_type == BufferType.Static:
            allocation.offset += data.size

    allocations = variable_allocations
    allocations.update(constant_allocations)

    layout = MemoryLayout(allocations, data)

    if flags.VISUALIZE_MEMORY_ALLOCATION:
        _visualize_allocation(operators, variables, layout)

    return layout


def _get_allocations(graph: Graph, operators: Sequence[Operator], variables: Sequence[Variable]) -> AllocationDict:
    T_LAST = len(operators)

    allocations = {}  # type: AllocationDict
    retain_count = {v: 0 for v in variables}  # type: Dict[Variable, int]
    allocated = set()  # type: Set[Variable]

    for v in traverse.filter_nodes(variables, ConstantVariable):
        # Constant variable cannot be released
        allocations[v] = Allocation(size=v.size, begin=0, end=T_LAST)
        allocated.add(v)

    for v in graph.inputs:
        # Input variable cannot be released
        allocations[v] = Allocation(size=v.size, begin=0, end=T_LAST)
        allocated.add(v)

    for v in graph.outputs:
        # Output variable cannot be released, but it's not needed to be allocated from the begin
        allocations[v] = Allocation(size=v.size, begin=_T_UNKNOWN, end=T_LAST)
        allocated.add(v)

    for t, op in enumerate(operators):
        for v in op.outputs.values():
            if v in allocated:
                # Allocation object is already created (output variable, etc.)
                if allocations[v].begin == _T_UNKNOWN:
                    allocations[v].begin = t

            else:
                # Create new allocation object
                allocations[v] = Allocation(size=v.size, begin=t, end=_T_UNKNOWN)
                retain_count[v] = len(v.input_to)
                allocated.add(v)

        for v in op.inputs.values():
            if v not in allocated:
                # Allocate
                allocations[v] = Allocation(size=v.size, begin=t, end=_T_UNKNOWN)
                retain_count[v] = len(v.input_to)
                allocated.add(v)

            if allocations[v].end != _T_UNKNOWN:
                # Release timing is already determined (input, output, or constant variable).
                continue

            # Release input variable
            retain_count[v] -= 1
            if retain_count[v] == 0:
                # `t + 1` means that `v` will be released *AFTER* `op` will be finished.
                allocations[v].end = t + 1

        for a in allocations.values():
            if a.begin == _T_UNKNOWN:
                a.begin = 0

            if a.end == _T_UNKNOWN:
                a.end = T_LAST

    return allocations


def _update_offset(allocations: AllocationDict):
    static_offset = 0
    dynamic_offset = 0

    for allocation in allocations.values():
        if allocation.buffer_type == BufferType.Static:
            allocation.offset = static_offset
            static_offset = _align(static_offset + allocation.size)

        else:
            allocation.offset = dynamic_offset
            dynamic_offset = (dynamic_offset + allocation.size)


def _update_constant_offset(allocations: AllocationDict):
    offset = 0
    data = []

    for v, a in allocations.items():  # type: ConstantVariable, Allocation
        data.append(v.data.flatten())
        a.offset = offset
        offset = _align(offset + v.size)

    return np.concatenate(data) if len(data) > 0 else np.empty((0,))


def _optimize_inplace(operators: Sequence[Operator], allocations_dict: AllocationDict):
    if not (flags.optimize.OPTIMIZE and flags.optimize.OPTIMIZE_MEMORY_ALLOCATION and flags.optimize.OPTIMIZE_INPLACE_OPERATION):
        console.debug('_optimize_inplace is skipped')
        return

    for op in operators:
        for attr in op.get_attribute(Inplace):  # type: Inplace
            a1 = allocations_dict[attr.get_input()]
            a2 = allocations_dict[attr.get_output()]
            if not Placeholder.check_resolved(a1.size) or not Placeholder.check_resolved(a2.size):
                continue

            _merge_allocation(allocations_dict, a1, a2)


def _optimize_buffer_reuse(allocations_dict: AllocationDict):
    """
    Optimize memory size by reusing buffer if available

    Algorithm:

    Considering 4 variables with follow size and lifetime.

        Size and Lifetime)

          var |size| Lifetime (t=0 -> ...)
          ----+----+---------------
            a |  5 | [0, 2)
            b |  4 | [2, 4)
            c |  2 | [3, 5)
            d |  1 | [6, 8)
            e |  3 | [0, 5)
          ----+----+---------------

    In this case, we want to get follow optimized allocation:

         ---------> address
    time
     |    aaaaa_e
     |    aaaaa_e
     |    bbbb__e
     |    bbbbcce
     |    ____cce
     V    d______
          d______

    First, construct "Merge Offset Table".

        table = {                           reduced_size = {
            a: {},                              a: {},
            b: { a: 0 },                        b: { a: 4 },
            c: { a: 0, b: 4 },                  c: { a: 2, b: 0 }
            d: { a: 0, b: 0, c: 0, e: 0 },      d: { a: 1, b: 1, c: 1, e: 1 },
            e: { a: 5, b: 4, c: 2, d: 0 }       e: { a: 0, b: 0, c: 0, d: 1 }
        }                                   }

    `table[x][y]` means offset value in case that variable `x` is merged into variable `y`. For example, when `b` is merged into
    (=reused the memory allocated for) `a`, offset value is `0` because they are not exist at same time. However, when `c` is merged into
    `b`, offset value is `4` because they are exist at same time (t=3).

    Next, for each mergeable pair, calculate the reduced size if two variables are merged. For example, if `b` is merged into `a`, the
    reduced size is `4`.

    Then merge the pair which has the largest reduced size. In this case such pair is `a` and `b`, and update the table.

        table = {                           reduced_size = {
            ab: {},                             ab: {},
            c: { ab: 4 },                       c: { ab: 1 }
            d: { ab: 0, c: 0, e: 0 },           d: { ab: 1, c: 1, e: 1 },
            e: { ab: 5, c: 2, d: 0 }            e: { ab: 0, c: 0, d: 1 }
        }                                   }

    Iterate this procedure until all variables are merged into single allocation.

    Merge `d` into `ab` with offset `0`:

        table = {                           reduced_size = {
            abd: {},                            abd: {},
            c: { abd: 4 },                      c: { abd: 1 },
            e: { abd: 5, c: 2 }                 e: { abd: 0, c: 0 }
        }                                   }

    Merge `c` into `abd` with offset `4`:

        table = {                           reduced_size = {
            abcd: {},                           abcd: {},
            e: { abcd: 5 }                      e: { abcd: 0 }
        }                                   }

    Merge `e` into `abcd` with offset `5`:

        table = {                           reduced_size = {
            abcde: {}                           abcde: {}
        }                                   }

    Finish.

    Time order:
        Build Table: O(N^2)
        Iteration: O(N) times
            update table: O(N)

        Total: O(N^2)
    """
    if not (flags.optimize.OPTIMIZE and flags.optimize.OPTIMIZE_MEMORY_ALLOCATION):
        console.debug('_optimize_buffer_reuse is skipped')
        return

    allocations = list(
        set(filter(lambda x: Placeholder.check_resolved(x.size) and Placeholder.check_resolved(x.offset), allocations_dict.values())))
    allocations = sorted(allocations, key=lambda a: a.size, reverse=True)

    # Construct offset table
    offset_table = {a2: {} for a2 in allocations}
    for i1, a1 in enumerate(allocations):
        for i2, a2 in enumerate(allocations[i1 + 1:]):
            # align offset as 16-byte alignment
            offset_table[a2][a1] = 0 if (a1.end <= a2.begin or a2.end <= a1.begin) else _align(a1.size)

    # Merge
    merge_tree = {}  # type: Dict[Allocation, Tuple[Allocation, int]]
    while len(offset_table) > 1:
        if len(offset_table) % 10 == 0:
            console.debug(f"Memory allocation optimization: {(1-len(offset_table)/len(allocations)) * 100:4.1f}% complete.")

        # Get max score pair
        max_score = -1
        max_a1 = None
        max_a2 = None
        for a2, a1s in offset_table.items():
            for a1, offset in a1s.items():
                score = max(min(a1.size - offset, a2.size), 0)
                if max_score < score:
                    max_score = score
                    max_a1 = a1
                    max_a2 = a2

        # Merge
        a1 = max_a1
        a2 = max_a2
        offset12 = offset_table[a2][a1]
        merge_tree[a2] = (a1, offset12)

        # Update offset table
        for a3, offset32 in offset_table[a2].items():
            if a1 in offset_table[a3]:
                # +-------+
                # |       V
                # a2->a3->a1
                #
                # condition
                # - min(a1.size - offset12, a2.size) > min(a1.size - offset13, a3.size)
                # - a2.size < a3.size < a1.size
                #
                # ==========================================================
                # case 1) offset13 < offset12 + a2.size
                #
                # before)
                # a1      |a1...................|
                # a2      <-offset12---->|a2...|
                # a3      <-offset13--------->|a3............|
                #                             <-offset23->|a2...|
                #
                # after)
                # a1      |a1...................|
                # a3      <-offset13------------>|a3............|
                #
                # ==========================================================
                #
                # before 2) offset13 > offset12 + a2.size
                # a1      |a1...................|
                # a2      <-offset12---->|a2...|
                # a3      <-offset13------------->|a3............|
                #                                 <-offset23->|a2...|
                #
                # after)
                # a1      |a1...................|
                # a3      <-offset13------------->|a3............|
                #
                offset_table[a3][a1] = max(offset_table[a3][a1], _align(offset12 + a2.size))

            elif a3 in offset_table[a1]:
                # +-------+
                # |       V
                # a2->a1->a3
                #
                # condition
                # - min(a1.size - offset12, a2.size) > min(a1.size - offset13, a3.size)
                # - a2.size < a1.size < a3.size
                #
                # ==========================================================
                # case 1) offset32 > offset31 + offset12
                #
                # before)
                #         <-offset32----------->|a2...|
                # a3      |a3..........|
                # a1      <-offset31--->|a1........|
                # a2                    <-offset12->|a2...|
                #
                # after) nothing changed
                # a3      |a3..........|
                # a1      <-offset31--->|a1........||a2...|
                #
                # ==========================================================
                # case 2) offset32 > offset31 + offset12
                #
                # before)
                #              <-offset32------------------->|a2...........................|
                # a3           |a3.........................|
                # a1           <-offset31->|a1........................................|
                # a2                        <-offset12->|a2...........................|
                #
                # after) offset31 = offset32 - offset12
                # a3      |a3.........................|
                # a1      <------offset31->|a1........................................|
                #
                offset_table[a1][a3] = max(offset_table[a1][a3], _align(offset32 - offset12))

        del offset_table[a2]
        for a3, a4s in offset_table.items():
            if a3 == a1:
                continue

            if a2 in a4s:
                if a1 in a4s:
                    # +-------+
                    # |       V
                    # a3->a2->a1

                    a4s[a1] = max(a4s[a1], offset12 + a4s[a2])
                    del a4s[a2]

                else:
                    raise NotImplementedError
                    # # a3->a2->a1
                    #
                    # a4s[a1] = offset12 + a4s[a2]
                    # del a4s[a2]

    console.debug(f"Memory allocation optimization: 100.0% complete.")

    if len(offset_table) > 0:
        # Shift allocation block to 0-offset.
        list(offset_table.keys())[0].offset = 0

    for a2, (a1, offset) in merge_tree.items():
        while a1 in merge_tree:
            a1, offset2 = merge_tree[a1]
            offset += offset2
        a2.offset = offset


def _merge_allocation(allocations: AllocationDict, a1: Allocation, a2: Allocation, a_new: Allocation = None):
    """
    merge two allocations into one new allocation
    """
    if a_new is None:
        a_new = Allocation(size=max(a1.size, a2.size), begin=min(a1.begin, a2.begin), end=max(a1.end, a2.end))

    for v, lifetime in allocations.items():
        if lifetime == a1 or lifetime == a2:
            allocations[v] = a_new


def _visualize_allocation(operators: Sequence[Operator], variables: Sequence[Variable], layout: MemoryLayout):
    UNIT_HEIGHT = 14
    total_size = layout.total_size - layout.data.size
    rendering_dict = {}  # type: Dict[Variable, RenderingInfo]

    class RenderingInfo:
        names: List[str]
        v1: Variable
        offset: int
        lifetime: Tuple[int, int]

        # noinspection PyShadowingNames
        def __init__(self, variable: Variable, allocation: Allocation):
            self.names = []
            self.variable = variable
            self.offset = allocation.offset - layout.data.size
            self.lifetime = (allocation.begin, allocation.end)

        @property
        def size(self):
            return self.variable.size

        @property
        def top(self):
            return f"{self.lifetime[0] * UNIT_HEIGHT}px"

        @property
        def height(self):
            return f"{(self.lifetime[1] - self.lifetime[0]) * UNIT_HEIGHT + 1}px"

        @property
        def left(self):
            return f"{self.offset * 100 / total_size}%"

        @property
        def width(self):
            return f"calc({self.size * 100 / total_size}% + 1px)"

        # noinspection PyMethodMayBeStatic
        def generate_html(self):
            return f"""<div class="Allocation {"Constant" if isinstance(self.variable, ConstantVariable) else ""}"
style="top: {self.top}; height: {self.height}; left: {self.left}; width: {self.width}" title="{", ".join(self.names)}
size: {self.size}
offset: {self.offset}
lifetime: {self.lifetime[0]} - {self.lifetime[1]}
">
    <p>{", ".join(self.names)}</p>
</div>"""

    html = """<html>
<head>
    <style>
        html, body {
            margin: 0;
        }
        body {
            padding: 32px;
            box-sizing: border-box;
        }
        .MemoryLayout {
            position: relative;
            background: #888;
            font-size: 8px;
        }
        .Allocation {
            position: absolute;
            border: 1px solid #000;
            display: block;
            padding: 0;
            box-sizing: border-box;
            overflow: hidden;
            background: #0f0;
        }
        .Constant {
            background: #ff0;
        }
        p {
            margin: 0;
            white-space: nowrap;
        }
    </style>
</head>
<body>
<header style="margin-bottom: 32px;">
    <h1>Memory Allocation Visualization</h1>
    <div style="margin: 32px 0">
        <p>Total allocation size: """ + str(total_size * 4) + """[byte]</p>
        <p># of allocated variables: """ + str(len(layout)) + """</p>
    </div>
    <div style="margin: 32px 0">
        <p>Vertical axis：time(from top(t=0) to bottom)</p>
        <p>Horizontal axis：memory address</p>
    </div>
</header>
    <div class="MemoryLayout" style="height: """ + str(UNIT_HEIGHT * len(operators) + 1) + """px;">
"""

    for v1 in variables:
        v2 = v1
        while "inplace_src" in v2.parameters:
            v2 = v2.parameters["inplace_src"]

        if v2 not in rendering_dict:
            if isinstance(v2, ConstantVariable):
                continue

            rendering_dict[v2] = RenderingInfo(v2, layout[v2])

        rendering_dict[v2].names.append(v1.name)

    for item in rendering_dict.values():
        html += item.generate_html()

    html += """
    </div>
</body>
</html>
"""

    with open('memory_visualize.html', "w+") as f:
        f.write(html)
