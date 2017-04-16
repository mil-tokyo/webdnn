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
    allocationDict: Dict[str, Allocation]

    def __init__(self,
                 size: int,
                 allocationDict: Dict[str, Allocation]):
        self.size = size
        self.allocationDict = allocationDict

    def _to_serializable_(self):
        return {
            "total_size": self.size,
            "allocation": {k: v for k, v in self.allocationDict.items()}
        }


class Allocator:
    layout: MemoryLayout

    @classmethod
    def allocate_params(cls, graph: Graph):
        offset = 0
        allocationDict = {}
        params = {}

        for node in graph.nodes:
            for layer in node.layer.iterate_self_and_children():
                for param_name, array in layer.weights.items():
                    key = layer.name + "/" + param_name
                    if key in allocationDict:
                        return

                    size = array.size
                    allocationDict[key] = Allocation(key, offset, size)
                    params[key] = array
                    offset += size

        layout = MemoryLayout(offset, allocationDict)

        buffer = np.zeros(layout.size, dtype=np.float32)
        for key, array in params.items():
            allocation = layout.allocationDict[key]
            buffer[allocation.offset:allocation.offset + allocation.size] = array.flatten()

        return layout, buffer

    @classmethod
    def allocate_variables(cls, graph: Graph):
        offset = 0
        allocationDict = {}

        for node in graph.nodes:
            for v in node.bottoms + node.tops:

                if v.name in allocationDict:
                    continue

                # noinspection PyTypeChecker
                size = int(np.prod(v.shape))
                allocationDict[v.name] = Allocation(v.name, offset, size)
                offset += size

        return MemoryLayout(offset, allocationDict)
