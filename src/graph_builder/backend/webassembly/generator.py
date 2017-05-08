"""
Descriptor Generator for WebAssembly

- kernel source generation
- schedule memory allocation
"""

import os.path as path
import subprocess
from typing import List

from graph_builder.backend.interface.graph_descriptor import IGraphExecutionData
from graph_builder.backend.webassembly.allocator import Allocator, MemoryLayout
from graph_builder.backend.webassembly.graph_descriptor import GraphDescriptor
from graph_builder.backend.webassembly.kernel import Kernel
from graph_builder.backend.webassembly.kernels.average_pooling_2d import average_pooling_2d
from graph_builder.backend.webassembly.kernels.axiswise_bias import axiswise_bias
from graph_builder.backend.webassembly.kernels.axiswise_scale import axiswise_scale
from graph_builder.backend.webassembly.kernels.col2im import col2im
from graph_builder.backend.webassembly.kernels.elementwise_sum import elementwise_sum
from graph_builder.backend.webassembly.kernels.elu import elu
from graph_builder.backend.webassembly.kernels.flatten import flatten
from graph_builder.backend.webassembly.kernels.im2col import im2col
from graph_builder.backend.webassembly.kernels.linear import linear
from graph_builder.backend.webassembly.kernels.local_response_normalization import local_response_normalization
from graph_builder.backend.webassembly.kernels.max_pooling_2d import max_pooling_2d
from graph_builder.backend.webassembly.kernels.relu import relu
from graph_builder.backend.webassembly.kernels.scalar_affine import scalar_affine
from graph_builder.backend.webassembly.kernels.sgemm import sgemm
from graph_builder.backend.webassembly.kernels.tanh import tanh
from graph_builder.backend.webassembly.operators.col2im import Col2Im
from graph_builder.backend.webassembly.operators.im2col import Im2Col
from graph_builder.backend.webassembly.operators.sgemm import Sgemm
from graph_builder.backend.webassembly.optimize_rules.webassembly_optimize_rule import WebassemblyOptimizeRule
from graph_builder.encoder.constant_encoder import ConstantEncoder
from graph_builder.graph import traverse
from graph_builder.graph.graph import Graph
from graph_builder.graph.operator import Operator
from graph_builder.graph.operators.average_pooling_2d import AveragePooling2D
from graph_builder.graph.operators.axiswise_bias import AxiswiseBias
from graph_builder.graph.operators.axiswise_scale import AxiswiseScale
from graph_builder.graph.operators.elementwise_sum import ElementwiseSum
from graph_builder.graph.operators.elu import Elu
from graph_builder.graph.operators.flatten import Flatten
from graph_builder.graph.operators.linear import Linear
from graph_builder.graph.operators.local_response_normalization import LocalResponseNormalization
from graph_builder.graph.operators.max_pooling_2d import MaxPooling2D
from graph_builder.graph.operators.relu import Relu
from graph_builder.graph.operators.scalar_affine import ScalarAffine
from graph_builder.graph.operators.tanh import Tanh
from graph_builder.util import flags
from graph_builder.util.json import json


class GraphExecutionData(IGraphExecutionData):
    descriptor: GraphDescriptor

    def __init__(self, descriptor: GraphDescriptor, constants: bytes):
        self.descriptor = descriptor
        self.constants = constants
        self.backend_suffix = "webassembly"

    def save(self, dirname: str):
        os.makedirs(dirname, exist_ok=True)

        with open(path.join(dirname, "graph_{}.json".format(self.backend_suffix)), "w") as f:
            json.dump(self.descriptor, f, indent=2)

        with open(path.join(dirname, "kernels_{}.cpp".format(self.backend_suffix)), "w") as f:
            f.write(self.descriptor.concat_kernel_sources())

        with open(path.join(dirname, "weight_{}.bin".format(self.backend_suffix)), "wb") as f:
            f.write(self.constants)

        self._compile(dirname)

    def _compile(self, dirname: str):
        # noinspection PyListCreation
        args = ["em++"]
        args.append(path.join(dirname, "kernels_{}.cpp".format(self.backend_suffix)))
        args.append("-O3")
        args.append("-std=c++11")
        args.append("-s")
        args.append("EXPORTED_FUNCTIONS=['_run','_init','_get_weight_buffer','_get_data_buffer']")
        args.append("-s")
        args.append("WASM=1")
        args.append("-s")
        args.append(f"TOTAL_MEMORY={self.descriptor.required_heap}")
        args.append("--pre-js")
        args.append(path.join(path.dirname(__file__), "webassembly_header.js"))
        args.append("-o")
        args.append(path.join(dirname, "kernels_{}.js".format(self.backend_suffix)))
        subprocess.check_call(args)


def generate(graph: Graph, constant_encoder_name: str = None) -> GraphExecutionData:
    graph, _ = WebassemblyOptimizeRule().optimize(graph)
    if flags.DEBUG:
        traverse.dump(graph)

    variables_layout, constants_layout, constants_data = Allocator.allocate(graph)
    if flags.DEBUG:
        print(
            f"[GraphDescriptorGeneratorWebassembly] constants_layout total size: {constants_data.size} * sizeof(float)")
        print(
            f"[GraphDescriptorGeneratorWebassembly] variables_layout total size: {variables_layout.size} * sizeof(float)")
    constant_encoder = ConstantEncoder.get_encoder(constant_encoder_name)
    constants_bytes = constant_encoder.encode(constants_layout, constants_data)
    if flags.DEBUG:
        print(f"[GraphDescriptorGeneratorWebGPU] constants encoded size: {len(constants_bytes)}")

    kernels = generate_kernels(graph, constants_layout, variables_layout)

    weight_data_size = (variables_layout.size + constants_layout.size) * 4  # sizeof(float)
    required_heap = (int(weight_data_size // 1048576) + 1 + 16) * 1048576  # required + 16MB

    descriptor = GraphDescriptor(
        kernels=kernels,
        constants_layout=constants_layout,
        variables_layout=variables_layout,
        inputs=graph.inputs,
        outputs=graph.outputs,
        constants_encoding=constant_encoder.name,
        required_heap=required_heap)

    return GraphExecutionData(descriptor, constants_bytes)


def generate_kernels(graph: Graph, constants_layout: MemoryLayout, variables_layout: MemoryLayout) -> List[Kernel]:
    kernels: List[Kernel] = []

    for op in traverse.listup_operators(graph):
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

        elif isinstance(op, ScalarAffine):
            kernels += scalar_affine(op, constants_layout, variables_layout)

        elif isinstance(op, Operator):
            if "custom_kernel" in op.parameters:
                kernels += op.parameters["custom_kernel"](op, constants_layout, variables_layout)
                continue

            raise NotImplementedError(f"{op} is Unknown for WebassemblyDescriptorGenerator")

        else:
            raise NotImplementedError(f"{op} is Unknown for WebassemblyDescriptorGenerator")

    return kernels
