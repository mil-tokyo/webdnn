from collections import OrderedDict
from datetime import datetime
from typing import Iterable, Dict, Set

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.fallback.kernel import Kernel
from webdnn.backend.interface.graph_descriptor import IGraphDescriptor
from webdnn.graph.placeholder import Placeholder
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable
from webdnn.util import json

source_header = """
dnn_fallback_kernel={
"""

source_footer = """
};
"""


class GraphDescriptor(json.SerializableMixin, IGraphDescriptor):
    kernels: Iterable[Kernel]
    memory_layout: MemoryLayout
    inputs: Iterable[Variable]
    outputs: Iterable[Variable]
    constants_encoding: str
    licenses: Dict[str, str]

    def __init__(self,
                 kernels: Iterable[Kernel],
                 memory_layout: MemoryLayout,
                 inputs: Iterable[Variable],
                 outputs: Iterable[Variable],
                 constants_encoding: str,
                 licenses: Dict[str, str]):
        self.kernels = kernels
        self.memory_layout = memory_layout
        self.inputs = inputs
        self.outputs = outputs
        self.constants_encoding = constants_encoding
        self.licenses = licenses

    def concat_kernel_sources(self):
        sources = OrderedDict()
        sources["header"] = source_header

        for kernel in self.kernels:
            for func_name, source in kernel.func_sources.items():
                if func_name in sources:
                    assert sources[func_name] == source
                else:
                    sources[func_name] = source

        sources["footer"] = source_footer
        combined_source = "\n".join(sources.values())

        return combined_source

    def get_all_placeholders(self):
        placeholders_set = set()  # type: Set[Placeholder]

        for kernel in self.kernels:
            for value in kernel.exec_info.call_option.values():
                if Placeholder.check_resolved(value):
                    continue

                placeholders_set.update(value.get_depend_placeholders())

        placeholders = {p.label: None for p in placeholders_set}

        return placeholders

    def _to_serializable_(self):
        placeholders = self.get_all_placeholders()

        return {
            "converted_at": int(datetime.timestamp(datetime.now())),
            "kernel_source": self.concat_kernel_sources(),
            "exec_infos": [kernel.exec_info for kernel in self.kernels],
            "weight_encoding": self.constants_encoding,
            "memory_layout": self.memory_layout,
            "placeholders": placeholders,
            "inputs": [self.memory_layout[v].name for v in self.inputs if not isinstance(v, ConstantVariable)],
            "outputs": [self.memory_layout[v].name for v in self.outputs],
            "licenses": self.licenses
        }
