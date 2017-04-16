# -*- coding:utf-8 -*-

"""
Kernel Builder for WebGPU

- kernel source generation
- schedule memory allocation
"""

import numpy as np

from graph_builder.backend.interface.kernel_builder import GraphDescriptorGenerator
from graph_builder.backend.webgpu.allocator import Allocator
from graph_builder.backend.webgpu.graph_descriptor_webgpu import GraphDescriptorWebGPU
from graph_builder.backend.webgpu.meta_buffer_injector import MetaBufferInjector
from graph_builder.backend.webgpu.operator_builder import OperatorBuilder
from graph_builder.frontend.graph import Graph
from graph_builder.util import flags


class GraphDescriptorGeneratorWebGPU(GraphDescriptorGenerator):
    allocator: Allocator
    weights_array: np.ndarray
    descriptor: GraphDescriptorWebGPU

    def __init__(self, graph: Graph):
        super().__init__(graph)
        self.weights_array = None
        self.descriptor = None

    def generate(self) -> GraphDescriptorWebGPU:
        batch_size = 1

        weights_layout, self.weights_array = Allocator.allocate_weights(self.graph)
        if flags.DEBUG:
            print(f"[GraphDescriptorGeneratorWebGPU] params_layout total size: {weights_layout.size} * sizeof(float)")

        variable_layout = Allocator.allocate_variables(self.graph)
        if flags.DEBUG:
            print(f"[GraphDescriptorGeneratorWebGPU] variable_layout total size: {variable_layout.size} * sizeof(float)")

        operators = OperatorBuilder.build_from_graph(self.graph)

        kernels = []
        for operator in operators:
            kernels.extend(operator.convert_to_kernels(
                batch_size,
                weights_layout,
                variable_layout,
                MetaBufferInjector()
            ))

        return GraphDescriptorWebGPU(
            kernels=kernels,
            weights_layout=weights_layout,
            variable_layout=variable_layout,
            inputs=self.graph.inputs,
            outputs=self.graph.outputs,
            batch_size=self.graph.batch_size
        )
