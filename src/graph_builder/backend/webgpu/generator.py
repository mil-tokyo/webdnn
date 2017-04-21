"""
Descriptor Generator for WebGPU

- kernel source generation
- schedule memory allocation
"""

import os.path as path
import subprocess
import tempfile as tmp
from typing import Tuple, List

import numpy as np

from graph_builder.backend.webgpu import kernels as K
from graph_builder.backend.webgpu import operators as webgpu_O
from graph_builder.backend.webgpu.allocator import Allocator, MemoryLayout
from graph_builder.backend.webgpu.graph_descriptor import GraphDescriptor
from graph_builder.backend.webgpu.kernel import Kernel
from graph_builder.backend.webgpu.webgpu_optimizer import WebGPUOptimizer
from graph_builder.graph import Operator, operators as O
from graph_builder.optimizer import util
from graph_builder.util import flags


def validate_kernel_source(descriptor: GraphDescriptor):
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


def generate(graph: Operator) -> Tuple[GraphDescriptor, np.array]:
    graph = WebGPUOptimizer().optimize(graph)
    if flags.DEBUG:
        util.dump(graph)

    variables_layout, constants_layout, constants_data = Allocator.allocate(graph)
    if flags.DEBUG:
        print(f"[GraphDescriptorGeneratorWebGPU] constants_layout total size: {constants_data.size} * sizeof(float)")
        print(f"[GraphDescriptorGeneratorWebGPU] variables_layout total size: {variables_layout.size} * sizeof(float)")

    kernels = generate_kernels(graph, constants_layout, variables_layout)

    descriptor = GraphDescriptor(
        kernels=kernels,
        constants_layout=constants_layout,
        variables_layout=variables_layout,
        inputs=graph.inputs,
        outputs=graph.outputs)

    if flags.backend.webgpu.VALIDATE_GENERATED_SOURCE:
        if flags.DEBUG:
            print("[GraphDescriptorGeneratorWebGPU] validate generated kernel source")

        validate_kernel_source(descriptor)

    return descriptor, constants_data


def generate_kernels(graph: Operator, constants_layout: MemoryLayout, variables_layout: MemoryLayout) -> List[Kernel]:
    kernels: List[Kernel] = []

    for op in util.listup_operator_in_order(graph):
        if isinstance(op, O.Compose):
            continue

        elif isinstance(op, O.Linear):
            kernels += K.linear(op, constants_layout, variables_layout)

        elif isinstance(op, O.AxiswiseBias):
            kernels += K.axiswise_bias(op, constants_layout, variables_layout)

        elif isinstance(op, O.Relu):
            kernels += K.relu(op, constants_layout, variables_layout)

        elif isinstance(op, O.Convolution2D):
            kernels += K.convolution_2d(op, constants_layout, variables_layout)

        elif isinstance(op, O.MaxPooling2D):
            kernels += K.max_pooling_2d(op, constants_layout, variables_layout)

        elif isinstance(op, O.AveragePooling2D):
            kernels += K.average_pooling_2d(op, constants_layout, variables_layout)

        elif isinstance(op, O.AxiswiseScale):
            kernels += K.axiswise_scale(op, constants_layout, variables_layout)

        elif isinstance(op, O.ElementwiseSum):
            kernels += K.elementwise_sum(op, constants_layout, variables_layout)

        elif isinstance(op, O.Flatten):
            kernels += K.flatten(op, constants_layout, variables_layout)

        elif isinstance(op, webgpu_O.Sgemm):
            kernels += K.sgemm(op, constants_layout, variables_layout)

        elif isinstance(op, webgpu_O.Im2Col):
            kernels += K.im2col(op, constants_layout, variables_layout)

        else:
            raise NotImplementedError(f"{op} is Unknown for WebGPUDescriptorGenerator")

    return kernels
