from typing import Dict, Iterable, Any

from webdnn.graph.variable import Variable
from webdnn.util import json


class KernelExecutionInfo(json.SerializableMixin):
    def __init__(self,
                 entry_func_name: str,
                 inputs: Iterable[Variable],
                 outputs: Iterable[Variable],
                 call_option: Dict[str, Any]):
        self.entry_func_name = entry_func_name
        self.inputs = inputs
        self.outputs = outputs
        self.call_option = call_option

    def _to_serializable_(self):
        return {
            "entry_func_name": self.entry_func_name,
            "inputs": [v.name for v in self.inputs],
            "outputs": [v.name for v in self.outputs],
            "call_option": self.call_option
        }


class Kernel:
    def __init__(self,
                 func_sources: Dict[str, str],
                 entry_func_name: str,
                 inputs: Iterable[Variable],
                 outputs: Iterable[Variable],
                 call_option: Dict[str, Any]):
        self.func_sources = func_sources
        self.exec_info = KernelExecutionInfo(
            entry_func_name=entry_func_name,
            inputs=inputs,
            outputs=outputs,
            call_option=call_option
        )
