from typing import Dict, Tuple, List, Set

import numpy as np

from webdnn.backend.interface.memory_layout import IMemoryLayout, IAllocation
from webdnn.graph import traverse
from webdnn.graph.graph import Graph
from webdnn.graph.variable import Variable
from webdnn.graph.variables.attributes.constant import Constant
from webdnn.graph.variables.constant_variable import ConstantVariable
from webdnn.util import json


class Allocation(json.SerializableMixin, IAllocation):
    variable: Variable
    offset: int

    def __init__(self,
                 variable: Variable,
                 offset: int):
        self.variable = variable
        self.offset = offset

    @property
    def size(self) -> int:
        return self.variable.size

    def _to_serializable_(self):
        return {
            "name": self.variable.parameters["name"],
            "offset": self.offset,
            "size": self.size
        }


class MemoryLayout(json.SerializableMixin, IMemoryLayout):
    def __init__(self):
        self.allocations = {}

    def _to_serializable_(self):
        return {
            "total_size": self.size,
            "allocations": {a.variable.parameters["name"]: a for _, a in self.allocations.items()}
        }

    def __getitem__(self, v: Variable):
        return self.allocations[v]

    def __contains__(self, v):
        return v in self.allocations

    def append(self, variable: Variable, offset: int = -1):
        if offset == -1:
            offset = self.size

        self.allocations[variable] = Allocation(variable, offset)

    @property
    def size(self) -> int:
        size = 0
        for v, a in self.allocations.items():
            size = max(a.offset, size) + a.size

        return size


class Allocator:
    layout: MemoryLayout

    @classmethod
    def allocate(cls, graph: Graph) -> Tuple[MemoryLayout, MemoryLayout]:
        variables = set(traverse.listup_variables(graph))
        for i, v in enumerate(variables):
            v.parameters["name"] = f"v{i}"
        constants = set(traverse.filter_nodes(variables, Constant))  # type: Set[ConstantVariable]
        variables = variables.difference(constants)

        variables = list(variables)
        constants = list(constants)

        constants_layout = cls.allocate_constants(constants)
        variables_layout = cls.allocate_variables(variables)
        return variables_layout, constants_layout

    @classmethod
    def allocate_constants(cls, constants: List[ConstantVariable]) -> MemoryLayout:
        layout = MemoryLayout()

        for constant in constants:
            if constant in layout:
                continue

            layout.append(constant)

        buffer = np.zeros(layout.size, dtype=np.float32)
        for constant in constants:
            allocation = layout[constant]
            buffer[allocation.offset:allocation.offset + allocation.size] = constant.data.flatten()

        layout.data = buffer
        return layout

    @classmethod
    def allocate_variables(cls, variables: List[Variable]) -> MemoryLayout:
        layout = MemoryLayout()

        for variable in variables:
            if variable in layout:
                continue

            layout.append(variable)

        return layout
