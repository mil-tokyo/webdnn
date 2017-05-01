from typing import Dict, Tuple, List, Set

import numpy as np

from graph_builder.graph.graph import Graph
from graph_builder.graph.operator import Operator
from graph_builder.graph.variable import Variable
from graph_builder.graph.variables.attributes.constant import Constant
from graph_builder.graph.variables.constant_variable import ConstantVariable
from graph_builder.optimize_rule import util
from graph_builder.util import json


class Allocation(json.SerializableMixin):
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


class MemoryLayout(json.SerializableMixin):
    size: int
    __dict__: Dict[Variable, Allocation]

    def __init__(self):
        self.__dict__ = {}

    def _to_serializable_(self):
        return {
            "total_size": self.size,
            "allocation": {a.variable.parameters["name"]: a for _, a in self.__dict__.items()}
        }

    def __getitem__(self, v: Variable):
        return self.__dict__[v]

    def __contains__(self, v):
        return v in self.__dict__

    def append(self, variable: Variable, offset: int = -1):
        if offset == -1:
            offset = self.size

        self.__dict__[variable] = Allocation(variable, offset)

    @property
    def size(self) -> int:
        size = 0
        for v, a in self.__dict__.items():
            size = max(a.offset, size) + a.size

        return size


class Allocator:
    layout: MemoryLayout

    @classmethod
    def allocate(cls, graph: Graph) -> Tuple[MemoryLayout, MemoryLayout, np.array]:
        variables = set(util.listup_variables(graph))
        for i, v in enumerate(variables):
            v.parameters["name"] = f"v{i}"
        constants = set(util.filter_nodes(variables, Constant))  # type: Set[ConstantVariable]
        variables = variables.difference(constants)

        variables = list(variables)
        constants = list(constants)

        constants_layout, data = cls.allocate_constants(constants)
        variables_layout = cls.allocate_variables(variables)
        return variables_layout, constants_layout, data

    @classmethod
    def allocate_constants(cls, constants: List[ConstantVariable]) -> Tuple[MemoryLayout, np.ndarray]:
        layout = MemoryLayout()

        for constant in constants:
            if constant in layout:
                continue

            layout.append(constant)

        buffer = np.zeros(layout.size, dtype=np.float32)
        for constant in constants:
            allocation = layout[constant]
            buffer[allocation.offset:allocation.offset + allocation.size] = constant.data.flatten()

        return layout, buffer

    @classmethod
    def allocate_variables(cls, variables: List[Variable]) -> MemoryLayout:
        layout = MemoryLayout()

        for variable in variables:
            if variable in layout:
                continue

            layout.append(variable)

        return layout
