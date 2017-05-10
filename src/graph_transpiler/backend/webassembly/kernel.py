from typing import Dict

import numpy as np

from graph_transpiler.util import json


class KernelExecutionInfo(json.SerializableMixin):
    entry_func_name: str
    meta_buffer: bytes

    def __init__(self,
                 entry_func_name: str,
                 meta_buffer: bytes):
        self.entry_func_name = entry_func_name
        self.meta_buffer = meta_buffer

    def _to_serializable_(self):
        return {
            "entry_func_name": self.entry_func_name,
            "meta_buffer": np.frombuffer(self.meta_buffer, dtype=np.uint8).tolist()
        }


class Kernel:
    func_sources: Dict[str, str]
    prototype_sources: Dict[str, str]
    exec_info: KernelExecutionInfo

    def __init__(self,
                 func_sources: Dict[str, str],
                 entry_func_name: str,
                 meta_buffer: bytes,
                 prototype_sources: Dict[str, str] = None):
        self.func_sources = func_sources
        self.prototype_sources = {} if prototype_sources is None else prototype_sources
        self.exec_info = KernelExecutionInfo(
            entry_func_name=entry_func_name,
            meta_buffer=meta_buffer
        )
