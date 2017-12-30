from typing import Dict, Tuple, List, Union, Set

import numpy as np

from webdnn.graph.placeholder import Placeholder
from webdnn.util import json


class GPUSize(json.SerializableMixin):
    width: Union[int, Placeholder]
    height: Union[int, Placeholder]
    depth: Union[int, Placeholder]

    def __init__(self, width: Union[int, Placeholder] = 1, height: Union[int, Placeholder] = 1, depth: Union[int, Placeholder] = 1):
        self.width = width
        self.height = height
        self.depth = depth

    def _to_serializable_(self):
        return {"width": self.width, "height": self.height, "depth": self.depth}

    def get_depend_placeholders(self) -> Set[Placeholder]:
        result = set()

        if not Placeholder.check_resolved(self.width):
            result.update(self.width.get_depend_placeholders())

        if not Placeholder.check_resolved(self.height):
            result.update(self.height.get_depend_placeholders())

        if not Placeholder.check_resolved(self.depth):
            result.update(self.depth.get_depend_placeholders())

        return result


class KernelExecutionInfo(json.SerializableMixin):
    entry_func_name: str
    threadgroups_per_grid: GPUSize
    threads_per_thread_group: GPUSize
    meta_buffer: bytes
    unresolved_value_list: List[Tuple[int, Placeholder]]

    def __init__(self,
                 entry_func_name: str,
                 threadgroups_per_grid: GPUSize,
                 threads_per_thread_group: GPUSize,
                 meta_buffer: bytes,
                 unresolved_value_list: List[Tuple[int, Placeholder]] = None):
        self.entry_func_name = entry_func_name
        self.threadgroups_per_grid = threadgroups_per_grid
        self.threads_per_thread_group = threads_per_thread_group
        self.meta_buffer = meta_buffer
        self.unresolved_value_list = [] if unresolved_value_list is None else unresolved_value_list  # type:List[Tuple[int, Placeholder]]

    def _to_serializable_(self):
        return {
            "entry_func_name": self.entry_func_name,
            "threadgroups_per_grid": self.threadgroups_per_grid,
            "threads_per_thread_group": self.threads_per_thread_group,
            "meta_buffer": np.frombuffer(self.meta_buffer, dtype=np.uint8).tolist(),
            "unresolved_value_list": [{"offset": v[0], "placeholder": v[1]} for v in self.unresolved_value_list]
        }


class Kernel:
    func_sources: Dict[str, str]
    exec_info: KernelExecutionInfo

    def __init__(self,
                 func_sources: Dict[str, str],
                 entry_func_name: str,
                 threadgroups_per_grid,
                 threads_per_thread_group,
                 meta_buffer: bytes,
                 unresolved_value_list: List[Tuple[int, Placeholder]] = None):
        self.func_sources = func_sources
        self.exec_info = KernelExecutionInfo(
            entry_func_name=entry_func_name,
            threadgroups_per_grid=threadgroups_per_grid,
            threads_per_thread_group=threads_per_thread_group,
            meta_buffer=meta_buffer,
            unresolved_value_list=[] if unresolved_value_list is None else unresolved_value_list
        )
