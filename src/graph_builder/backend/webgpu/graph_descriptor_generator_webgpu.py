# -*- coding:utf-8 -*-

"""
Kernel Builder for WebGPU

- kernel source generation
- schedule memory allocation
"""

import numpy as np
from typing import Dict

from graph_builder.graph import Graph
from graph_builder.backend.interface.kernel_builder import GraphDescriptorGenerator
from graph_builder.backend.webgpu.allocator_webgpu import AllocatorWebGPU, WorkspaceLayoutWebGPU
from graph_builder.backend.webgpu.graph_descriptor_webgpu import GraphDescriptorWebGPU
from graph_builder.backend.webgpu.kernel_builder import KernelBuilder


class GraphDescriptorGeneratorWebGPU(GraphDescriptorGenerator):
    allocator: AllocatorWebGPU
    params_array: np.ndarray
    descriptor: GraphDescriptorWebGPU

    def __init__(self, graph: Graph):
        super().__init__(graph)
        self.allocator = AllocatorWebGPU()
        self.params_array = None
        self.descriptor = None

    def generate(self) -> GraphDescriptorWebGPU:
        params = self._enum_params()
        params_layout, self.params_array = self.allocator.allocate_params(params)

        variables = self._enum_variables()
        variable_layout = self.allocator.allocate_variables(variables)

        kernels = self._get_layers_kernels(params_layout, variable_layout)

        return GraphDescriptorWebGPU(
            kernels=kernels,
            params_layout=params_layout,
            variable_layout=variable_layout,
            inputs=self.graph.inputs,
            outputs=self.graph.outputs,
            batch_size=self.graph.batch_size
        )

    def _enum_params(self):
        params = {}  # type: Dict[(str, str), array]

        # FIXME: layerとnodeが混在しているのを治す
        for node in self.graph.nodes:
            for layer in node.layer.iterate_self_and_children():
                node_name = layer.name
                for param_name, array in layer.weights.items():
                    params[(node_name, param_name)] = array

        return params

    def _enum_variables(self):
        variables = {}  # name => DNNVariable
        for node in self.graph.nodes:
            for v in node.bottoms + node.tops:
                variables[v.name] = v
                # TODO: temporary variable (im2colのバッファなど、サイズが実装依存なのでbuilder内でサイズを決めて確保)
        return variables

    def _get_layers_kernels(self, params_layout: WorkspaceLayoutWebGPU, variable_layout: WorkspaceLayoutWebGPU):
        all_kernels = []

        for node in self.graph.nodes:
            kernels = KernelBuilder.build(
                node.layer,
                self.graph.batch_size,
                node.bottoms,
                node.tops,
                params_layout,
                variable_layout
            )

            all_kernels.extend(kernels)

        return all_kernels
