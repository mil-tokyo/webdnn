from typing import Dict
import numpy as np
from graph_builder.kernel_builder.interface.allocator import WorkspaceLayout
from graph_builder.util import json


class Allocation(json.SerializableMixin):
    name: str
    offset: int
    size: int

    def __init__(self, name: str, offset: int, size: int):
        self.name = name
        self.offset = offset
        self.size = size

    def _to_serializable_(self):
        return {
            "name": self.name,
            "offset": self.offset,
            "size": self.size
        }


class WorkspaceLayoutWebGPU(WorkspaceLayout):
    size: int
    allocationDict: Dict[str, Allocation]

    def __init__(self, size: int, allocationDict: Dict[str, Allocation]):
        self.size = size
        self.allocationDict = allocationDict

    def _to_serializable_(self):
        return {
            "total_size": self.size,
            "allocation": {k: v for k, v in self.allocationDict.items()}
        }


class AllocatorWebGPU:
    layout: WorkspaceLayoutWebGPU

    # noinspection PyMethodMayBeStatic
    def allocate_params(self, weights):
        offset = 0
        allocationDict = {}

        for weight_id, array in weights.items():
            size = array.size
            weight_name = "/".join(weight_id)
            allocationDict[weight_name] = Allocation(weight_name, offset, size)
            offset += size

        layout = WorkspaceLayoutWebGPU(offset, allocationDict)

        buffer = np.zeros(layout.size, dtype=np.float32)
        for weight_id, array in weights.items():
            allocation = layout.allocationDict["/".join(weight_id)]
            buffer[allocation.offset:allocation.offset + allocation.size] = array.flatten()

        return layout, buffer

    # noinspection PyMethodMayBeStatic
    def allocate_variables(self, variables):
        """
        変数の割付アドレスを決める
        """
        offset = 0
        allocationDict = {}

        for name, array in variables.items():
            # noinspection PyTypeChecker
            size = int(np.prod(array.shape))
            allocationDict[name] = Allocation(name, offset, size)
            offset += size

        return WorkspaceLayoutWebGPU(offset, allocationDict)
