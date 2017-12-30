from collections import OrderedDict
from datetime import datetime
from typing import Iterable, Dict, List, Set, Tuple

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.interface.graph_descriptor import IGraphDescriptor
from webdnn.backend.webgpu.kernel import Kernel
from webdnn.graph.placeholder import Placeholder
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable
from webdnn.util import json, flags

source_header = f"""
#include <metal_stdlib>
using namespace metal;

#define OPTIMIZE {"1" if flags.optimize.OPTIMIZE else "0"}
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
        func_sources = OrderedDict()

        # with open(path.join(path.dirname(__file__), "./libs.metal")) as f:
        #     libs = f.read()
        libs = ""

        for kernel in self.kernels:
            for func_name, source in kernel.func_sources.items():
                if func_name in func_sources:
                    assert func_sources[func_name] == source
                else:
                    func_sources[func_name] = source

        combined_source = \
            source_header + \
            libs + \
            "\n".join(func_sources.values())

        return combined_source

    def get_all_placeholders(self):
        unresolved_variables = []  # type: List[Tuple[int, Placeholder]]
        placeholders_set = set()  # type: Set[Placeholder]

        for kernel in self.kernels:
            unresolved_variables += kernel.exec_info.unresolved_value_list

        for offset, v in unresolved_variables:
            placeholders_set.update(v.get_depend_placeholders())

        for kernel in self.kernels:
            placeholders_set.update(kernel.exec_info.threadgroups_per_grid.get_depend_placeholders())
            placeholders_set.update(kernel.exec_info.threads_per_thread_group.get_depend_placeholders())

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
