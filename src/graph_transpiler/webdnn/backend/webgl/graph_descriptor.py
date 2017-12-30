from collections import OrderedDict
from datetime import datetime
from typing import Iterable, Dict, Any

from webdnn.backend.interface.graph_descriptor import IGraphDescriptor
from webdnn.backend.webgl.allocator import WebGLMemoryLayout
from webdnn.backend.webgl.kernel import Kernel
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable
from webdnn.util import json


class GraphDescriptor(json.SerializableMixin, IGraphDescriptor):
    def __init__(self,
                 kernels: Iterable[Kernel],
                 memory_layout: WebGLMemoryLayout,
                 inputs: Iterable[Variable],
                 outputs: Iterable[Variable],
                 constants_encoding: str,
                 constants_map: Any,
                 licenses: Dict[str, str]):
        self.kernels = kernels
        self.memory_layout = memory_layout
        self.inputs = inputs
        self.outputs = outputs
        self.constants_encoding = constants_encoding
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
            "converted_at": int(datetime.timestamp(datetime.now())),
            "inputs": [v.parameters["name"] for v in self.inputs if not isinstance(v, ConstantVariable)],
            "outputs": [v.parameters["name"] for v in self.outputs],
            "memory_layout": self.memory_layout,
            "weight_encoding": self.constants_encoding,
            "placeholders": placeholders,

            "shader_sources": self.concat_kernel_sources(),
            "exec_infos": [kernel.exec_info for kernel in self.kernels],
            "constants_map": self.constants_map,
            "licenses": self.licenses,
        }
