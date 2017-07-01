from typing import Dict, List, Tuple

import numpy as np

from webdnn.graph.placeholder import Placeholder
from webdnn.util import json


class KernelExecutionInfo(json.SerializableMixin):
    entry_func_name: str
    meta_buffer: bytes

    def __init__(self,
                 entry_func_name: str,
                 meta_buffer: bytes,
                 unresolved_value_list: List[Tuple[int, Placeholder]] = None):
        self.entry_func_name = entry_func_name
        self.meta_buffer = meta_buffer
        self.unresolved_value_list = [] if unresolved_value_list is None else unresolved_value_list  # type:List[Tuple[int, Placeholder]]

    def _to_serializable_(self):
        return {
            "entry_func_name": self.entry_func_name,
            "meta_buffer": np.frombuffer(self.meta_buffer, dtype=np.uint8).tolist(),
            "unresolved_value_list": [{"offset": v[0], "placeholder": v[1]} for v in self.unresolved_value_list]
        }


class Kernel:
    func_sources: Dict[str, str]
    exec_info: KernelExecutionInfo

    def __init__(self,
                 func_sources: Dict[str, str],
                 entry_func_name: str,
                 meta_buffer: bytes,
                 unresolved_value_list: List[Tuple[int, Placeholder]] = None):
        self.func_sources = func_sources
        self.exec_info = KernelExecutionInfo(
            entry_func_name=entry_func_name,
            meta_buffer=meta_buffer,
            unresolved_value_list=[] if unresolved_value_list is None else unresolved_value_list
        )
