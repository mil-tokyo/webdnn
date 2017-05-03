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

from graph_builder.backend.webassembly.allocator import Allocator, MemoryLayout
from graph_builder.backend.webassembly.graph_descriptor import GraphDescriptor
from graph_builder.backend.webassembly.kernel import Kernel
from graph_builder.backend.webassembly.kernels.affine_transform import affine_transform
from graph_builder.backend.webassembly.kernels.average_pooling_2d import average_pooling_2d
from graph_builder.backend.webassembly.kernels.axiswise_bias import axiswise_bias
from graph_builder.backend.webassembly.kernels.axiswise_scale import axiswise_scale
from graph_builder.backend.webassembly.kernels.col2im import col2im
from graph_builder.backend.webassembly.kernels.elementwise_sum import elementwise_sum
from graph_builder.backend.webassembly.kernels.elu import elu
from graph_builder.backend.webassembly.kernels.flatten import flatten
from graph_builder.backend.webassembly.kernels.im2col import im2col
from graph_builder.backend.webassembly.kernels.linear import linear
from graph_builder.backend.webassembly.kernels.max_pooling_2d import max_pooling_2d
from graph_builder.backend.webassembly.kernels.relu import relu
from graph_builder.backend.webassembly.kernels.sgemm import sgemm
from graph_builder.backend.webassembly.kernels.tanh import tanh
from graph_builder.backend.webassembly.kernels.local_response_normalization import local_response_normalization
from graph_builder.backend.webassembly.operators.affine_transform import AffineTransform
from graph_builder.backend.webassembly.operators.col2im import Col2Im
from graph_builder.backend.webassembly.operators.im2col import Im2Col
from graph_builder.backend.webassembly.operators.sgemm import Sgemm
from graph_builder.backend.webassembly.optimize_rules.webgpu_optimize_rule import WebGPUOptimizeRule
from graph_builder.graph.graph import Graph
from graph_builder.graph.operator import Operator
from graph_builder.graph.operators.average_pooling_2d import AveragePooling2D
from graph_builder.graph.operators.axiswise_bias import AxiswiseBias
from graph_builder.graph.operators.axiswise_scale import AxiswiseScale
from graph_builder.graph.operators.elementwise_sum import ElementwiseSum
from graph_builder.graph.operators.elu import Elu
from graph_builder.graph.operators.flatten import Flatten
from graph_builder.graph.operators.linear import Linear
from graph_builder.graph.operators.max_pooling_2d import MaxPooling2D
from graph_builder.graph.operators.relu import Relu
from graph_builder.graph.operators.tanh import Tanh
from graph_builder.graph.operators.local_response_normalization import LocalResponseNormalization
from graph_builder.encoder.constant_encoder import ConstantEncoder
from graph_builder.optimize_rule import util
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


def generate(graph: Graph, constant_encoder_name: str = None) -> Tuple[GraphDescriptor, bytes]:
    graph, _ = WebGPUOptimizeRule().optimize(graph)
    if flags.DEBUG:
        util.dump(graph)

    variables_layout, constants_layout, constants_data = Allocator.allocate(graph)
    if flags.DEBUG:
        print(f"[GraphDescriptorGeneratorWebGPU] constants_layout total size: {constants_data.size} * sizeof(float)")
        print(f"[GraphDescriptorGeneratorWebGPU] variables_layout total size: {variables_layout.size} * sizeof(float)")
    constant_encoder = ConstantEncoder.get_encoder(constant_encoder_name)
    constants_bytes = constant_encoder.encode(constants_layout, constants_data)
    if flags.DEBUG:
        print(f"[GraphDescriptorGeneratorWebGPU] constants encoded size: {len(constants_bytes)}")

    kernels = generate_kernels(graph, constants_layout, variables_layout)

    descriptor = GraphDescriptor(
        kernels=kernels,
        constants_layout=constants_layout,
        variables_layout=variables_layout,
        inputs=graph.inputs,
        outputs=graph.outputs,
        constants_encoding=constant_encoder.name)

    if flags.backend.webassembly.VALIDATE_GENERATED_SOURCE:
        if flags.DEBUG:
            print("[GraphDescriptorGeneratorWebGPU] validate generated kernel source")

        validate_kernel_source(descriptor)

    return descriptor, constants_bytes


def generate_kernels(graph: Graph, constants_layout: MemoryLayout, variables_layout: MemoryLayout) -> List[Kernel]:
    kernels: List[Kernel] = []

    for op in util.listup_operators(graph):
        if isinstance(op, Linear):
            kernels += linear(op, constants_layout, variables_layout)

        elif isinstance(op, AxiswiseBias):
            kernels += axiswise_bias(op, constants_layout, variables_layout)

        elif isinstance(op, Relu):
            kernels += relu(op, constants_layout, variables_layout)

        elif isinstance(op, Elu):
            kernels += elu(op, constants_layout, variables_layout)

        elif isinstance(op, Tanh):
            kernels += tanh(op, constants_layout, variables_layout)

        elif isinstance(op, LocalResponseNormalization):
            kernels += local_response_normalization(op, constants_layout, variables_layout)

        elif isinstance(op, MaxPooling2D):
            kernels += max_pooling_2d(op, constants_layout, variables_layout)

        elif isinstance(op, AveragePooling2D):
            kernels += average_pooling_2d(op, constants_layout, variables_layout)

        elif isinstance(op, AxiswiseScale):
            kernels += axiswise_scale(op, constants_layout, variables_layout)

        elif isinstance(op, ElementwiseSum):
            kernels += elementwise_sum(op, constants_layout, variables_layout)

        elif isinstance(op, Flatten):
            kernels += flatten(op, constants_layout, variables_layout)

        elif isinstance(op, Sgemm):
            kernels += sgemm(op, constants_layout, variables_layout)

        elif isinstance(op, Im2Col):
            kernels += im2col(op, constants_layout, variables_layout)

        elif isinstance(op, Col2Im):
            kernels += col2im(op, constants_layout, variables_layout)

        elif isinstance(op, AffineTransform):
            kernels += affine_transform(op, constants_layout, variables_layout)

        elif isinstance(op, Operator):
            if "custom_kernel" in op.parameters:
                kernels += op.parameters["custom_kernel"](op, constants_layout, variables_layout)
                continue

            raise NotImplementedError(f"{op} is Unknown for WebGPUDescriptorGenerator")

        else:
            raise NotImplementedError(f"{op} is Unknown for WebGPUDescriptorGenerator")

    return kernels
