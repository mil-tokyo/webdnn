from collections import OrderedDict
from typing import Dict, Tuple, List
import numpy as np

from graph_builder.frontend.graph import Graph, Variable, GraphNode
from graph_builder.util import json, flags


class Allocation(json.SerializableMixin):
    name: str
    offset: int
    size: int

    def __init__(self,
                 name: str,
                 offset: int,
                 size: int):
        self.name = name
        self.offset = offset
        self.size = size

    def _to_serializable_(self):
        return {
            "name": self.name,
            "offset": self.offset,
            "size": self.size
        }


class MemoryLayout(json.SerializableMixin):
    size: int
    allocation_dict: Dict[str, Allocation]

    def __init__(self,
                 size: int,
                 allocationDict: Dict[str, Allocation]):
        self.size = size
        self.allocation_dict = allocationDict

    def _to_serializable_(self):
        return {
            "total_size": self.size,
            "allocation": {k: v for k, v in self.allocation_dict.items()}
        }


class Allocator:
    layout: MemoryLayout

    @classmethod
    def allocate_weights(cls, graph: Graph) -> Tuple[MemoryLayout, np.ndarray]:
        offset = 0
        allocation_dict = {}
        weights = {}

        for node in graph.nodes:
            for layer in node.layer.iterate_self_and_children():
                for param_name, array in layer.weights.items():
                    key = layer.name + "/" + param_name
                    if key in allocation_dict:
                        continue

                    size = array.size
                    allocation_dict[key] = Allocation(key, offset, size)
                    weights[key] = array
                    offset += size

        layout = MemoryLayout(offset, allocation_dict)

        buffer = np.zeros(layout.size, dtype=np.float32)
        for key, array in weights.items():
            allocation = layout.allocation_dict[key]
            buffer[allocation.offset:allocation.offset + allocation.size] = array.flatten()

        return layout, buffer

    @classmethod
    def allocate_variables(cls, graph: Graph):
        if flags.optimize.MINIMIZE_VARIABLE_ALLOCATION:

            # list-up lifetime of all variables
            # [born_node_index, born_node, dead_node_index, dead_node]
            lifetime_table: Dict[Variable: Tuple[int, GraphNode, int, GraphNode]] = OrderedDict()
            for var in graph.inputs + graph.outputs:
                lifetime_table[var] = [0, graph.nodes[0], len(graph.nodes), graph.nodes[-1]]

            for node_index, node in enumerate(graph.nodes):
                for var in node.bottoms + node.tops:
                    if var in lifetime_table:
                        lifetime = lifetime_table[var]

                        if node_index < lifetime[0]:
                            lifetime[0] = node_index
                            lifetime[1] = node

                        if node_index > lifetime[2]:
                            lifetime[2] = node_index
                            lifetime[3] = node

                    else:
                        lifetime_table[var] = [node_index, node, node_index, node]

            # table of the variables which is released after the graph node.
            deadtime_table: Dict[GraphNode, List[Variable]] = {}
            for var, (_, _, _, node) in lifetime_table.items():
                if node in deadtime_table:
                    deadtime_table[node].append(var)

                else:
                    deadtime_table[node] = [var]

            if flags.DEBUG:
                for var, lifetime in lifetime_table.items():
                    print(f"[Allocator] variable lifetime: {var.name} = ({lifetime[0]}, {lifetime[2]})")

            # list contains information of partial free space
            # tuple[0]: offset of the partial space
            # tuple[1]: size of the partial space
            free_list = []  # type: List[Tuple[int, int]]
            total_size = 0
            allocation_dict = {}
            for node_index, node in enumerate(graph.nodes):
                for var, lifetime in lifetime_table.items():
                    if var.name in allocation_dict or lifetime[0] > node_index:
                        continue

                    # noinspection PyTypeChecker
                    required_size = int(np.prod(var.shape))

                    for partial_space in free_list:
                        offset, size = partial_space
                        if required_size <= size:
                            free_list.remove(partial_space)
                            free_list.append((offset + required_size, size - required_size))
                            break

                    else:
                        offset = total_size
                        total_size += required_size

                    allocation_dict[var.name] = Allocation(var.name, offset, required_size)

                if node in deadtime_table:
                    for var in deadtime_table[node]:
                        allocation = allocation_dict[var.name]
                        free_list.append((allocation.offset, allocation.size))

                        # TODO: resolve fragmentation

            return MemoryLayout(total_size, allocation_dict)

        else:
            offset = 0
            allocation_dict = {}

            for node in graph.nodes:
                for var in node.bottoms + node.tops:

                    if var.name in allocation_dict:
                        continue

                    # noinspection PyTypeChecker
                    size = int(np.prod(var.shape))
                    allocation_dict[var.name] = Allocation(var.name, offset, size)
                    offset += size

            return MemoryLayout(offset, allocation_dict)
