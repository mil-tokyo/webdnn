from typing import Dict, List, Set, Union, Sequence

import numpy as np

from webdnn.backend.code_generator.allocator import MemoryLayout, Allocation, BufferType
from webdnn.backend.webgl.attributes.channel_mode import ChannelMode, ChannelModeEnum
from webdnn.backend.webgl.attributes.texture_shape import TextureShape
from webdnn.graph import traverse
from webdnn.graph.graph import Graph
from webdnn.graph.operator import Operator
from webdnn.graph.placeholder import Placeholder
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable

IntLike = Union[int, Placeholder]
WebGLAllocationDict = Dict[Variable, "WebGLAllocation"]
_T_UNKNOWN = -1

_count = 0


def _name(prefix: str):
    global _count
    _count += 1
    return f"{prefix}{_count}"


def _align(offset: int, unit: int = 1):
    return ((offset + unit - 1) // unit) * unit


class WebGLAllocation(Allocation):
    def __init__(self, size: IntLike, width: IntLike, height: IntLike, channel_mode: ChannelModeEnum, begin: int = _T_UNKNOWN, end: int = _T_UNKNOWN, name: str = None):
        super(WebGLAllocation, self).__init__(size=size, offset=-1, begin=begin, end=end, name=name)
        self.width = width
        self.height = height
        self.channel_mode = channel_mode

    def _to_serializable_(self):
        return {
            "name": self.name,
            "offset": -1,
            "size": self.size,
            "width": self.width,
            "height": self.height,
            "channel_mode": self.channel_mode.name
        }


class WebGLMemoryLayout(MemoryLayout):
    def _to_serializable_(self):
        # WebGLMemoryLayout does not support total length
        allocations = set(self.allocations.values())

        return {
            "static": {
                "size": -1,
                "allocations": {a.name: a for a in allocations if a.buffer_type == BufferType.Static}
            },
            "dynamic": {
                "size": -1,
                "allocations": {a.name: a for a in allocations if a.buffer_type == BufferType.Dynamic}
            },
            "mapping": {v.name: a.name for v, a in self.allocations.items()}
        }

    def __len__(self):
        return len(self.allocations)

    def __getitem__(self, v: Variable):
        return self.allocations[v]

    def __contains__(self, v: Variable):
        return v in self.allocations

    @property
    def total_size(self) -> IntLike:
        # WebGLMemoryLayout does not support total length
        raise NotImplementedError

    @property
    def static_size(self) -> int:
        # WebGLMemoryLayout does not support total length
        raise NotImplementedError

    @property
    def dynamic_size(self) -> IntLike:
        # WebGLMemoryLayout does not support total length
        raise NotImplementedError


def allocate(graph: Graph) -> WebGLMemoryLayout:
    nodes = traverse.listup_nodes(graph)
    operators = traverse.filter_nodes(nodes, Operator)
    variables = traverse.filter_nodes(nodes, Variable)

    for i, v in enumerate(variables):
        if v.name is None:
            v.name = _name("v")

    dynamic_constants = traverse.filter_nodes([v for v in variables if not Placeholder.check_resolved(v.size)], ConstantVariable)
    assert len(dynamic_constants) == 0, f"ConstantVariable with unresolved placeholder shape is detected: f{dynamic_constants}"

    allocations = _get_allocations(graph, operators, variables)
    _optimize_buffer_reuse(allocations)

    variable_allocations = {v: allocations[v] for v in variables if not isinstance(v, ConstantVariable)}
    constant_allocations = {v: allocations[v] for v in variables if isinstance(v, ConstantVariable)}

    data = _update_constant_offset(constant_allocations)

    allocations = variable_allocations
    allocations.update(constant_allocations)

    layout = WebGLMemoryLayout(allocations, data)
    return layout


def _get_allocations(graph: Graph, operators: Sequence[Operator], variables: Sequence[Variable]) -> WebGLAllocationDict:
    T_LAST = len(operators)

    allocations = {}  # type: WebGLAllocationDict
    retain_count = {v: 0 for v in variables}  # type: Dict[Variable, int]
    allocated = set()  # type: Set[Variable]

    for v in traverse.filter_nodes(variables, ConstantVariable):
        # Constant variable cannot be released
        height, width = TextureShape.get(v)
        width = (width + ChannelMode.elements_per_pixel(v) - 1) // ChannelMode.elements_per_pixel(v)
        allocations[v] = WebGLAllocation(size=v.size, width=width, height=height, channel_mode=ChannelMode.get(v), begin=0, end=T_LAST, name=v.name)
        allocated.add(v)

    for v in graph.inputs:
        # Input variable cannot be released
        height, width = TextureShape.get(v)
        width = (width + ChannelMode.elements_per_pixel(v) - 1) // ChannelMode.elements_per_pixel(v)
        allocations[v] = WebGLAllocation(size=v.size, width=width, height=height, channel_mode=ChannelMode.get(v), begin=0, end=T_LAST, name=v.name)
        allocated.add(v)

    for v in graph.outputs:
        # Output variable cannot be released, but it's not needed to be allocated from the begin
        height, width = TextureShape.get(v)
        width = (width + ChannelMode.elements_per_pixel(v) - 1) // ChannelMode.elements_per_pixel(v)
        allocations[v] = WebGLAllocation(size=v.size, width=width, height=height, channel_mode=ChannelMode.get(v), begin=_T_UNKNOWN, end=T_LAST, name=v.name)
        allocated.add(v)

    for t, op in enumerate(operators):
        for v in op.outputs.values():
            if v in allocated:
                # Allocation object is already created (output variable, etc.)
                if allocations[v].begin == _T_UNKNOWN:
                    allocations[v].begin = t

            else:
                # Create new allocation object
                height, width = TextureShape.get(v)
                width = (width + ChannelMode.elements_per_pixel(v) - 1) // ChannelMode.elements_per_pixel(v)
                allocations[v] = WebGLAllocation(size=v.size, width=width, height=height, channel_mode=ChannelMode.get(v), begin=t, end=_T_UNKNOWN, name=v.name)
                retain_count[v] = len(v.input_to)
                allocated.add(v)

        for v in op.inputs.values():
            if v not in allocated:
                # Allocate
                height, width = TextureShape.get(v)
                width = (width + ChannelMode.elements_per_pixel(v) - 1) // ChannelMode.elements_per_pixel(v)
                allocations[v] = WebGLAllocation(size=v.size, width=width, height=height, channel_mode=ChannelMode.get(v), begin=t, end=_T_UNKNOWN, name=v.name)
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

    return allocations


def _optimize_buffer_reuse(allocations_dict: WebGLAllocationDict):
    texture_table = {}  # type: Dict[str, List[WebGLAllocation]]
    allocation2variables = {a: [v] for v, a in allocations_dict.items()}

    def texture_key(a: WebGLAllocation):
        return f"{a.height}x{a.width}"

    for a in allocations_dict.values():
        if a.buffer_type == BufferType.Dynamic:
            continue

        if texture_key(a) not in texture_table:
            texture_table[texture_key(a)] = []
        texture_table[texture_key(a)].append(a)

    for key in texture_table.keys():
        allocations = sorted(texture_table[key], key=lambda a: a.end)

        for a1 in allocations:
            if a1.buffer_type == BufferType.Dynamic:
                continue

            for a2 in allocations:
                if a2.buffer_type == BufferType.Dynamic:
                    continue

                if a1 is a2:
                    continue

                if not (a2.end < a1.begin or a1.end < a2.begin):
                    # lifetime of a1 and a2 is overlapped
                    continue

                allocations.remove(a2)
                for v in allocation2variables[a2]:
                    allocations_dict[v] = a1
                    allocation2variables[a1].append(v)

                a1.begin = min(a1.begin, a2.begin)
                a1.end = max(a1.end, a2.end)


def _update_constant_offset(allocations: WebGLAllocationDict):
    offset = 0
    data = []

    for v, a in allocations.items():  # type: ConstantVariable, WebGLAllocation
        data.append(v.data.flatten())
        a.offset = offset
        offset = _align(offset + v.size)

    return np.concatenate(data) if len(data) > 0 else np.empty((0,))
