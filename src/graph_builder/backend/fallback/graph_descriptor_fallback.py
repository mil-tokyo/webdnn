from collections import OrderedDict
from typing import Iterable, Dict

from graph_builder.backend.fallback.allocator import MemoryLayout
from graph_builder.backend.fallback.kernel import Kernel
from graph_builder.frontend.graph import Variable
from graph_builder.util import json

source_header = """
dnn_fallback_kernel={
"""

source_footer = """
};
"""

class GraphDescriptorFallback(json.SerializableMixin):
    kernels: Iterable[Kernel]
    params_layout: MemoryLayout
    variable_layout: MemoryLayout
    inputs: Iterable[Variable]
    outputs: Iterable[Variable]
    batch_size: int

    def __init__(self,
                 kernels: Iterable[Kernel],
                 params_layout: MemoryLayout,
                 variable_layout: MemoryLayout,
                 inputs: Iterable[Variable],
                 outputs: Iterable[Variable],
                 batch_size: int):
        self.kernels = kernels
        self.params_layout = params_layout
        self.variable_layout = variable_layout
        self.inputs = inputs
        self.outputs = outputs
        self.batch_size = batch_size

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

    def _to_serializable_(self):
        return {
            "kernel_source": self.concat_kernel_sources(),
            "exec_infos": [kernel.exec_info for kernel in self.kernels],
            "weight_allocation": self.params_layout,  # FIXME: weight => params へrename
            "variable_allocation": self.variable_layout,
            "inputs": [v.name for v in self.inputs],
            "outputs": [v.name for v in self.outputs],
            "batch_size": self.batch_size
        }
