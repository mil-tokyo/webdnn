from collections import OrderedDict
from typing import Iterable

from graph_builder.backend.webassembly.allocator import MemoryLayout
from graph_builder.backend.webassembly.kernel import Kernel
from graph_builder.graph.variable import Variable
from graph_builder.graph.variables.attributes.constant import Constant
from graph_builder.optimize_rule import util
from graph_builder.util import json

source_header = """
#include <metal_stdlib>
using namespace metal;


"""


class GraphDescriptor(json.SerializableMixin):
    kernels: Iterable[Kernel]
    constants_layout: MemoryLayout
    variables_layout: MemoryLayout
    inputs: Iterable[Variable]
    outputs: Iterable[Variable]
    constants_encoding: str

    def __init__(self,
                 kernels: Iterable[Kernel],
                 constants_layout: MemoryLayout,
                 variables_layout: MemoryLayout,
                 inputs: Iterable[Variable],
                 outputs: Iterable[Variable],
                 constants_encoding: str):
        self.kernels = kernels
        self.constants_layout = constants_layout
        self.variables_layout = variables_layout
        self.inputs = inputs
        self.outputs = outputs
        self.constants_encoding = constants_encoding

    def concat_kernel_sources(self):
        func_sources = OrderedDict()
        prototype_sources = OrderedDict()

        for kernel in self.kernels:
            for func_name, source in kernel.func_sources.items():
                if func_name in func_sources:
                    assert func_sources[func_name] == source
                else:
                    func_sources[func_name] = source

            for func_name, source in kernel.prototype_sources.items():
                if func_name in prototype_sources:
                    assert prototype_sources[func_name] == source
                else:
                    prototype_sources[func_name] = source

        combined_source = \
            source_header + \
            "\n".join(prototype_sources.values()) + \
            "\n".join(func_sources.values())

        return combined_source

    def _to_serializable_(self):
        return {
            "kernel_source": self.concat_kernel_sources(),
            "exec_infos": [kernel.exec_info for kernel in self.kernels],
            "weight_allocation": self.constants_layout,
            "weight_encoding": self.constants_encoding,
            "variable_allocation": self.variables_layout,
            "inputs": [v.parameters["name"] for v in self.inputs if not util.check_attribute_match(v, Constant)],
            "outputs": [v.parameters["name"] for v in self.outputs]
        }
