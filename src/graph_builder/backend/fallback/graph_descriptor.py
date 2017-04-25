from collections import OrderedDict
from typing import Iterable, Dict

from graph_builder.backend.fallback.allocator import MemoryLayout
from graph_builder.backend.fallback.kernel import Kernel
from graph_builder.graph.variable import Variable
from graph_builder.graph.variables.attributes.constant import Constant
from graph_builder.optimize_rule import util
from graph_builder.util import json

source_header = """
dnn_fallback_kernel={
"""

source_footer = """
};
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

        sources["footer"] = source_footer
        combined_source = "\n".join(sources.values())

        return combined_source

    def _to_serializable_(self):
        return {
            "kernel_source": self.concat_kernel_sources(),
            "exec_infos": [kernel.exec_info for kernel in self.kernels],
            "weight_allocation": self.constants_layout,
            "variable_allocation": self.variables_layout,
            "inputs": [v.parameters["name"] for v in self.inputs.values() if not util.check_attribute_match(v, Constant)],
            "outputs": [v.parameters["name"] for v in self.outputs.values()]
        }
