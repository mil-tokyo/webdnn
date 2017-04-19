from collections import OrderedDict
from typing import Iterable, Dict

from graph_builder.backend.webgpu.allocator import MemoryLayout
from graph_builder.backend.webgpu.kernel import Kernel
from graph_builder.graph import Variable
from graph_builder.graph.variables import attributes as VA
from graph_builder.optimizer import util
from graph_builder.util import json

source_header = """
#include <metal_stdlib>
using namespace metal;


"""


class GraphDescriptor(json.SerializableMixin):
    kernels: Iterable[Kernel]
    constants_layout: MemoryLayout
    variables_layout: MemoryLayout
    inputs: Dict[str, Variable]
    outputs: Dict[str, Variable]

    def __init__(self,
                 kernels: Iterable[Kernel],
                 constants_layout: MemoryLayout,
                 variables_layout: MemoryLayout,
                 inputs: Dict[str, Variable],
                 outputs: Dict[str, Variable]):
        self.kernels = kernels
        self.constants_layout = constants_layout
        self.variables_layout = variables_layout
        self.inputs = inputs
        self.outputs = outputs

    def concat_kernel_sources(self):
        sources = OrderedDict()
        sources["header"] = source_header

        for kernel in self.kernels:
            for func_name, source in kernel.func_sources.items():
                if func_name in sources:
                    assert sources[func_name] == source
                else:
                    sources[func_name] = source

        combined_source = "\n".join(sources.values())

        return combined_source

    def _to_serializable_(self):
        return {
            "kernel_source": self.concat_kernel_sources(),
            "exec_infos": [kernel.exec_info for kernel in self.kernels],
            "weight_allocation": self.constants_layout,
            "variable_allocation": self.variables_layout,
            "inputs": [v.parameters["name"] for v in self.inputs.values() if not util.check_attribute_match(v, VA.Constant)],
            "outputs": [v.parameters["name"] for v in self.outputs.values()],
            "batch_size": 1  # FIXME
        }
