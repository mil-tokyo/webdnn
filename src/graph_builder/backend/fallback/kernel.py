from typing import Dict, Iterable

from graph_builder.util import json


class KernelExecutionInfo(json.SerializableMixin):
    entry_func_name: str
    inputs: Iterable[str]
    outputs: Iterable[str]
    weights: Iterable[str]
    call_option: Dict[str, object]

    def __init__(self,
                 entry_func_name: str,
                 inputs: Iterable[str],
                 outputs: Iterable[str],
                 weights: Iterable[str],
                 call_option: Dict[str, object]):
        self.entry_func_name = entry_func_name
        self.inputs = inputs
        self.outputs = outputs
        self.weights = weights
        self.call_option = call_option

    def _to_serializable_(self):
        return {
            "entry_func_name": self.entry_func_name,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "weights": self.weights,
            "call_option": self.call_option
        }


class Kernel:
    func_sources: Dict[str, str]
    exec_info: KernelExecutionInfo

    def __init__(self,
                 func_sources: Dict[str, str],
                 entry_func_name: str,
                 inputs: Iterable[str],
                 outputs: Iterable[str],
                 weights: Iterable[str],
                 call_option: Dict[str, object]):
        self.func_sources = func_sources
        self.exec_info = KernelExecutionInfo(
            entry_func_name=entry_func_name,
            inputs=inputs,
            outputs=outputs,
            weights=weights,
            call_option=call_option
        )
