from typing import Dict, Tuple, List, Set

import numpy as np

from graph_builder.graph.graph import Variable, Operator
from graph_builder.graph.variables import Constant, attributes as VA
from graph_builder.optimizer import util
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
    def allocate(cls, graph: Operator) -> Tuple[MemoryLayout, MemoryLayout, np.array]:
        variables = util.listup_variables(graph, remove_alias=True)
        for i, v in enumerate(variables):
            v.parameters["name"] = f"v{i}"

        constants = set(util.filter_nodes(variables, VA.Constant))  # type: Set[Constant]
        variables = variables.difference(constants)

        variables = list(variables)
        constants = list(constants)

        constants_layout, data = cls.allocate_constants(constants)
        variables_layout = cls.allocate_variables(variables)
        return variables_layout, constants_layout, data

    @classmethod
    def allocate_constants(cls, constants: List[Constant]) -> Tuple[MemoryLayout, np.ndarray]:
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
        # if flags.optimize.MINIMIZE_VARIABLE_ALLOCATION:
        #
        #     # list-up lifetime of all variables
        #     # [born_node_index, born_node, dead_node_index, dead_node]
        #     lifetime_table: Dict[Variable: Tuple[int, GraphNode, int, GraphNode]] = OrderedDict()
        #     for var in graph.inputs + graph.outputs:
        #         lifetime_table[var] = [0, graph.nodes[0], len(graph.nodes), graph.nodes[-1]]
        #
        #     for node_index, node in enumerate(graph.nodes):
        #         for var in node.bottoms + node.tops:
        #             if var in lifetime_table:
        #                 lifetime = lifetime_table[var]
        #
        #                 if node_index < lifetime[0]:
        #                     lifetime[0] = node_index
        #                     lifetime[1] = node
        #
        #                 if node_index > lifetime[2]:
        #                     lifetime[2] = node_index
        #                     lifetime[3] = node
        #
        #             else:
        #                 lifetime_table[var] = [node_index, node, node_index, node]
        #
        #     # table of the variables which is released after the graph node.
        #     deadtime_table: Dict[GraphNode, List[Variable]] = {}
        #     for var, (_, _, _, node) in lifetime_table.items():
        #         if node in deadtime_table:
        #             deadtime_table[node].append(var)
        #
        #         else:
        #             deadtime_table[node] = [var]
        #
        #     if flags.DEBUG:
        #         for var, lifetime in lifetime_table.items():
        #             print(f"[Allocator] variable lifetime: {var.name} = ({lifetime[0]}, {lifetime[2]})")
        #
        #     # list contains information of partial free space
        #     # tuple[0]: offset of the partial space
        #     # tuple[1]: size of the partial space
        #     free_list = []  # type: List[Tuple[int, int]]
        #     total_size = 0
        #     allocation_dict = {}
        #     for node_index, node in enumerate(graph.nodes):
        #         for var, lifetime in lifetime_table.items():
        #             if var.name in allocation_dict or lifetime[0] > node_index:
        #                 continue
        #
        #             # noinspection PyTypeChecker
        #             required_size = int(np.prod(var.shape))
        #
        #             for partial_space in free_list:
        #                 offset, size = partial_space
        #                 if required_size <= size:
        #                     free_list.remove(partial_space)
        #                     free_list.append((offset + required_size, size - required_size))
        #                     break
        #
        #             else:
        #                 offset = total_size
        #                 total_size += required_size
        #
        #             allocation_dict[var.name] = Allocation(var.name, offset, required_size)
        #
        #         if node in deadtime_table:
        #             for var in deadtime_table[node]:
        #                 allocation = allocation_dict[var.name]
        #                 free_list.append((allocation.offset, allocation.size))
        #
        #                 # TODO: resolve fragmentation
        #
        #     return MemoryLayout(total_size, allocation_dict)
        #
        # else:
        layout = MemoryLayout()

        for variable in variables:
            if variable in layout:
                continue

            layout.append(variable)

        return layout
