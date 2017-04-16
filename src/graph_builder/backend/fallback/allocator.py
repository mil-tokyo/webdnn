from typing import Dict
import numpy as np

from graph_builder.frontend.graph import Graph
from graph_builder.util import json


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
                 allocation_dict: Dict[str, Allocation]):
        self.size = size
        self.allocation_dict = allocation_dict

    def _to_serializable_(self):
        return {
            "total_size": self.size,
            "allocation": {k: v for k, v in self.allocation_dict.items()}
        }


class Allocator:
    layout: MemoryLayout

    @classmethod
    def allocate_weights(cls, graph: Graph):
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
        offset = 0
        allocation_dict = {}

        for node in graph.nodes:
            for v in node.bottoms + node.tops:

                if v.name in allocation_dict:
                    continue

                # noinspection PyTypeChecker
                size = int(np.prod(v.shape))
                allocation_dict[v.name] = Allocation(v.name, offset, size)
                offset += size

        return MemoryLayout(offset, allocation_dict)
