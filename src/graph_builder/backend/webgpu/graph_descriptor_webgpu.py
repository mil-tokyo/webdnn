from collections import OrderedDict

from typing import Iterable

from graph_builder.graph import Variable
from graph_builder.backend.webgpu.allocator_webgpu import WorkspaceLayoutWebGPU
from graph_builder.backend.webgpu.kernel import Kernel
from graph_builder.backend.interface.graph_descriptor import GraphDescriptor

source_header = """
#include <metal_stdlib>
using namespace metal;


"""


class GraphDescriptorWebGPU(GraphDescriptor):
    kernels: Iterable[Kernel]
    params_layout: WorkspaceLayoutWebGPU
    variable_layout: WorkspaceLayoutWebGPU
    inputs: Iterable[Variable]
    outputs: Iterable[Variable]
    batch_size: int

    def __init__(self,
                 kernels: Iterable[Kernel],
                 params_layout: WorkspaceLayoutWebGPU,
                 variable_layout: WorkspaceLayoutWebGPU,
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

        combined_source = "\n".join(sources.values())

        return combined_source

    def _to_serializable_(self):
        return {
            "kernel_source": self.concat_kernel_sources(),
            "exec_infos": [kernel.exec_info for kernel in self.kernels],
            "weight_allocation": self.params_layout,        #FIXME: weight => params へrename
            "variable_allocation": self.variable_layout,
            "inputs": [v.name for v in self.inputs],
            "outputs": [v.name for v in self.outputs],
            "batch_size": self.batch_size
        }
