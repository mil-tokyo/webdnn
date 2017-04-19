# -*- coding:utf-8 -*-

"""
Kernel Builder for WebGPU

- kernel source generation
- schedule memory allocation
"""

import os.path as path
import subprocess
import tempfile as tmp

import numpy as np

from graph_builder.backend.interface.kernel_builder import GraphDescriptorGenerator
from graph_builder.backend.webgpu.allocator import Allocator
from graph_builder.backend.webgpu.graph_descriptor_webgpu import GraphDescriptorWebGPU
from graph_builder.backend.webgpu.meta_buffer_injector import MetaBufferInjector
from graph_builder.backend.webgpu.operator_builder import OperatorBuilder
from graph_builder.frontend.graph import Operator
from graph_builder.util import flags


def validate_kernel_source(descriptor: GraphDescriptorWebGPU):
    # FIXME: WebGPU supports multi shader languages, but this test supposes the language as METAL.

    source = descriptor.concat_kernel_sources()

    with tmp.TemporaryDirectory() as tmpdir:
        source_path = path.join(tmpdir, "kernel.metal")
        lib_path = path.join(tmpdir, "kernel.air")

        with open(source_path, "w+") as f:
            f.write(source)

        result = subprocess.run(["xcrun", "-sdk", "macosx", "metal", source_path, "-o", lib_path])
        if result.returncode != 0:
            print("Generated kernel source is invalid.")
            exit(result.returncode)


class GraphDescriptorGeneratorWebGPU(GraphDescriptorGenerator):
    allocator: Allocator
    weights_array: np.ndarray
    descriptor: GraphDescriptorWebGPU

    def __init__(self, graph: Operator):
        super().__init__(graph)
        self.weights_array = None
        self.descriptor = None

    def generate(self) -> GraphDescriptorWebGPU:
        graph = self.graph

        # TODO: backend optimization
        # optimize(self.graph)

        # すでに最適化は完了しているものとして、あとは愚直に生成する
        variables, constants = Optimizer.util.correct_variables(graph)

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

        descriptor = GraphDescriptorWebGPU(
            kernels=kernels,
            weights_layout=weights_layout,
            variable_layout=variable_layout,
            inputs=self.graph.inputs,
            outputs=self.graph.outputs,
            batch_size=self.graph.batch_size
        )

        if flags.backend.webgpu.VALIDATE_GENERATED_SOURCE:
            if flags.DEBUG:
                print("[GraphDescriptorGeneratorWebGPU] validate generated kernel source")

            validate_kernel_source(descriptor)

        return descriptor
