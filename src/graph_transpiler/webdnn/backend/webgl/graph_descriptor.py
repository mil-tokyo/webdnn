from collections import OrderedDict
from typing import Iterable, Dict, Any

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.interface.graph_descriptor import IGraphDescriptor
from webdnn.backend.webgl import generator
from webdnn.backend.webgl.kernel import Kernel
from webdnn.graph import traverse
from webdnn.graph.variable import Variable
from webdnn.graph.variables.attributes.constant import Constant
from webdnn.util import json


class GraphDescriptor(json.SerializableMixin, IGraphDescriptor):
    def __init__(self,
                 kernels: Iterable[Kernel],
                 memory_layout: MemoryLayout,
                 inputs: Iterable[Variable],
                 outputs: Iterable[Variable],
                 constants_encoding: str,
                 allocations: Dict[Variable, "generator.WebGLAllocation"],
                 constants_map: Any,
                 licenses: Dict[str, str]):
        self.kernels = kernels
        self.memory_layout = memory_layout
        self.inputs = inputs
        self.outputs = outputs
        self.constants_encoding = constants_encoding
        self.allocations = allocations
        self.constants_map = constants_map
        self.licenses = licenses

    def concat_kernel_sources(self):
        func_sources = OrderedDict()

        for kernel in self.kernels:
            func_name = kernel.exec_info.shader_name
            source = kernel.source

            if func_name in func_sources:
                assert func_sources[func_name] == source
            else:
                func_sources[func_name] = source

        return dict(func_sources)

    def get_all_placeholders(self):
        # FIXME
        raise NotImplementedError

    def _to_serializable_(self):
        # placeholders = self.get_all_placeholders()
        placeholders = []

        return {
            "inputs": [v.parameters["name"] for v in self.inputs if not traverse.check_attribute_match(v, Constant)],
            "outputs": [v.parameters["name"] for v in self.outputs],
            "memory_layout": self.memory_layout,
            "weight_encoding": self.constants_encoding,
            "placeholders": placeholders,

            "shader_sources": self.concat_kernel_sources(),
            "exec_infos": [kernel.exec_info for kernel in self.kernels],
            "variables": {v.name: {
                "variable_size": v.size,
                "allocation_name": a.name
            } for v, a in self.allocations.items()},  # type: Variable, generator.WebGLAllocation
            "allocations": {a.name: {
                "allocation_size": a.size,
                "channel_mode": a.channel_mode.name
            } for a in self.allocations.values()},
            "constants_map": self.constants_map,
            "licenses": self.licenses,
        }
