from typing import Dict, Tuple, List

import numpy as np

from webdnn.graph.place_holder import PlaceHolder
from webdnn.util import json


class GPUSize(json.SerializableMixin):
    width: int
    height: int
    depth: int

    def __init__(self, width: int = 1, height: int = 1, depth: int = 1):
        self.width = width
        self.height = height
        self.depth = depth

    def _to_serializable_(self):
        return {"width": self.width, "height": self.height, "depth": self.depth}


class KernelExecutionInfo(json.SerializableMixin):
    entry_func_name: str
    threadgroups_per_grid: GPUSize
    threads_per_thread_group: GPUSize
    meta_buffer: bytes
    unresolved_value_list: List[Tuple[int, PlaceHolder]]

    def __init__(self,
                 entry_func_name: str,
                 threadgroups_per_grid: GPUSize,
                 threads_per_thread_group: GPUSize,
                 meta_buffer: bytes,
                 unresolved_value_list: List[Tuple[int, PlaceHolder]] = None):
        self.entry_func_name = entry_func_name
        self.threadgroups_per_grid = threadgroups_per_grid
        self.threads_per_thread_group = threads_per_thread_group
        self.meta_buffer = meta_buffer
        self.unresolved_value_list = [] if unresolved_value_list is None else unresolved_value_list  # type:List[Tuple[int, PlaceHolder]]

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
                 unresolved_value_list: List[Tuple[int, PlaceHolder]] = None):
        self.func_sources = func_sources
        self.exec_info = KernelExecutionInfo(
            entry_func_name=entry_func_name,
            threadgroups_per_grid=threadgroups_per_grid,
            threads_per_thread_group=threads_per_thread_group,
            meta_buffer=meta_buffer,
            unresolved_value_list=[] if unresolved_value_list is None else unresolved_value_list
        )
