from collections import OrderedDict
from typing import Iterable, Dict

from webdnn.backend.fallback.allocator import MemoryLayout
from webdnn.backend.fallback.kernel import Kernel
from webdnn.backend.interface.graph_descriptor import IGraphDescriptor
from webdnn.graph import traverse
from webdnn.graph.variable import Variable
from webdnn.graph.variables.attributes.constant import Constant
from webdnn.util import json

source_header = """
dnn_fallback_kernel={
"""

source_footer = """
};
"""


class GraphDescriptor(json.SerializableMixin, IGraphDescriptor):
    kernels: Iterable[Kernel]
    constants_layout: MemoryLayout
    variables_layout: MemoryLayout
    inputs: Iterable[Variable]
    outputs: Iterable[Variable]
    constants_encoding: str
    licenses: Dict[str, str]

    def __init__(self,
                 kernels: Iterable[Kernel],
                 constants_layout: MemoryLayout,
                 variables_layout: MemoryLayout,
                 inputs: Iterable[Variable],
                 outputs: Iterable[Variable],
                 constants_encoding: str,
                 licenses: Dict[str, str]):
        self.kernels = kernels
        self.constants_layout = constants_layout
        self.variables_layout = variables_layout
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

    def _to_serializable_(self):
        return {
            "kernel_source": self.concat_kernel_sources(),
            "exec_infos": [kernel.exec_info for kernel in self.kernels],
            "weight_allocation": self.constants_layout,
            "weight_encoding": self.constants_encoding,
            "variable_allocation": self.variables_layout,
            "inputs": [v.parameters["name"] for v in self.inputs if not traverse.check_attribute_match(v, Constant)],
            "outputs": [v.parameters["name"] for v in self.outputs],
            "licenses": self.licenses
        }
