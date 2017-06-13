"""
Descriptor Generator for WebAssembly

- kernel source generation
- schedule memory allocation
"""

import os
import os.path as path
import subprocess
import sys
import platform
from typing import List

from webdnn.backend.code_generator.allocator import Allocator, MemoryLayout
from webdnn.backend.interface.graph_descriptor import IGraphExecutionData
from webdnn.backend.webassembly.graph_descriptor import GraphDescriptor
from webdnn.backend.webassembly.kernel import Kernel
from webdnn.backend.webassembly.kernels.average_pooling_2d import average_pooling_2d
from webdnn.backend.webassembly.kernels.axiswise_bias import axiswise_bias
from webdnn.backend.webassembly.kernels.axiswise_scale import axiswise_scale
from webdnn.backend.webassembly.kernels.col2im import col2im
from webdnn.backend.webassembly.kernels.concat import concat
from webdnn.backend.webassembly.kernels.elementwise_sum import elementwise_sum
from webdnn.backend.webassembly.kernels.elu import elu
from webdnn.backend.webassembly.kernels.sigmoid import sigmoid
from webdnn.backend.webassembly.kernels.flatten import flatten
from webdnn.backend.webassembly.kernels.im2col import im2col
from webdnn.backend.webassembly.kernels.linear import linear
from webdnn.backend.webassembly.kernels.local_response_normalization import local_response_normalization
from webdnn.backend.webassembly.kernels.max_pooling_2d import max_pooling_2d
from webdnn.backend.webassembly.kernels.relu import relu
from webdnn.backend.webassembly.kernels.scalar_affine import scalar_affine
from webdnn.backend.webassembly.kernels.sgemm import sgemm
from webdnn.backend.webassembly.kernels.tanh import tanh
from webdnn.backend.webassembly.kernels.embedding import embedding
from webdnn.backend.webassembly.kernels.lstm import lstm
from webdnn.backend.webassembly.operators.col2im import Col2Im
from webdnn.backend.webassembly.operators.im2col import Im2Col
from webdnn.backend.webassembly.operators.sgemm import Sgemm
from webdnn.backend.webassembly.optimize_rules.webassembly_optimize_rule import WebassemblyOptimizeRule
from webdnn.encoder.constant_encoder import ConstantEncoder
from webdnn.graph import traverse
from webdnn.graph.graph import Graph
from webdnn.graph.operator import Operator
from webdnn.graph.operators.average_pooling_2d import AveragePooling2D
from webdnn.graph.operators.axiswise_bias import AxiswiseBias
from webdnn.graph.operators.axiswise_scale import AxiswiseScale
from webdnn.graph.operators.concat import Concat
from webdnn.graph.operators.elementwise_sum import ElementwiseSum
from webdnn.graph.operators.elu import Elu
from webdnn.graph.operators.sigmoid import Sigmoid
from webdnn.graph.operators.flatten import Flatten
from webdnn.graph.operators.linear import Linear
from webdnn.graph.operators.local_response_normalization import LocalResponseNormalization
from webdnn.graph.operators.max_pooling_2d import MaxPooling2D
from webdnn.graph.operators.relu import Relu
from webdnn.graph.operators.scalar_affine import ScalarAffine
from webdnn.graph.operators.tanh import Tanh
from webdnn.graph.operators.embedding import Embedding
from webdnn.graph.operators.lstm import LSTM
from webdnn.util import flags
from webdnn.util.json import json


class GraphExecutionData(IGraphExecutionData):
    descriptor: GraphDescriptor

    def __init__(self, descriptor: GraphDescriptor, constants: bytes):
        self.descriptor = descriptor
        self.constants = constants
        self.backend_suffix = "webassembly"
        self.platform_windows = platform.system() == "Windows"  # workaround for PATH problem

    def save(self, dirname: str):
        os.makedirs(dirname, exist_ok=True)

        with open(path.join(dirname, "graph_{}.json".format(self.backend_suffix)), "w") as f:
            json.dump(self.descriptor, f, indent=2)

        with open(path.join(dirname, "kernels_{}.cpp".format(self.backend_suffix)), "w") as f:
            f.write(self.descriptor.concat_kernel_sources())

        with open(path.join(dirname, "weight_{}.bin".format(self.backend_suffix)), "wb") as f:
            f.write(self.constants)

        self._compile(dirname)
        self._compile_fallback_asmjs(dirname)

    def _compile(self, dirname: str):
        # noinspection PyListCreation
        args = ["em++"]
        args.append(path.join(dirname, "kernels_{}.cpp".format(self.backend_suffix)))
        args.append("-O3")
        args.append("-std=c++11")
        args.append("-s")
        args.append("EXPORTED_FUNCTIONS=['_run','_init','_get_data_buffer']")
        args.append("-s")
        args.append("WASM=1")
        args.append("-s")
        args.append(f"TOTAL_MEMORY={self.descriptor.required_heap}")
        args.append("--pre-js")
        args.append(path.join(path.dirname(__file__), "webassembly_header.js"))
        args.append("-o")
        args.append(path.join(dirname, "kernels_{}.js".format(self.backend_suffix)))
        try:
            subprocess.check_call(args, shell=self.platform_windows)
        except Exception as ex:
            sys.stderr.write("Executing em++ command failed." +
                             " Make sure emscripten is properly installed and environment variables are set.\n")
            raise ex

    def _compile_fallback_asmjs(self, dirname: str):
        # noinspection PyListCreation
        backend_suffix = "asmjs"
        args = ["em++"]
        args.append(path.join(dirname, "kernels_{}.cpp".format(self.backend_suffix)))
        args.append("-O3")
        args.append("-std=c++11")
        args.append("-s")
        args.append("EXPORTED_FUNCTIONS=['_run','_init','_get_data_buffer']")
        args.append("-s")
        args.append(f"TOTAL_MEMORY={self.descriptor.required_heap}")
        args.append("--pre-js")
        args.append(path.join(path.dirname(__file__), "webassembly_header.js"))
        args.append("-o")
        args.append(path.join(dirname, "kernels_{}.js".format(backend_suffix)))
        try:
            subprocess.check_call(args, shell=self.platform_windows)
        except Exception as ex:
            sys.stderr.write("Executing em++ command failed." +
                             " Make sure emscripten is properly installed and environment variables are set.\n")
            raise ex


def generate(graph: Graph, constant_encoder_name: str = None) -> GraphExecutionData:
    graph, _ = WebassemblyOptimizeRule().optimize(graph)
    if flags.DEBUG:
        traverse.dump(graph)

    memory_layout = Allocator.allocate(graph)
    if flags.DEBUG:
        print(f"[GraphDescriptorGeneratorWebassembly] memory_layout total size: {memory_layout.size * 4}")

    constant_encoder = ConstantEncoder.get_encoder(constant_encoder_name)
    constants_bytes = constant_encoder.encode(memory_layout)

    if flags.DEBUG:
        print(f"[GraphDescriptorGeneratorWebassembly] constants encoded size: {len(constants_bytes)}")

    kernels = generate_kernels(graph, memory_layout)

    required_heap = (int((memory_layout.size * 4) // (16 * 1024 * 1024)) + 2) * 16 * 1024 * 1024  # required + 16MB

    descriptor = GraphDescriptor(
        kernels=kernels,
        memory_layout=memory_layout,
        inputs=graph.inputs,
        outputs=graph.outputs,
        constants_encoding=constant_encoder.name,
        required_heap=required_heap,
        licenses=graph.licenses)

    return GraphExecutionData(descriptor, constants_bytes)


def generate_kernels(graph: Graph, memory_layout: MemoryLayout) -> List[Kernel]:
    kernels: List[Kernel] = []

    for op in traverse.listup_operators(graph):
        if isinstance(op, Linear):
            kernels += linear(op, memory_layout)

        elif isinstance(op, AxiswiseBias):
            kernels += axiswise_bias(op, memory_layout)

        elif isinstance(op, Relu):
            kernels += relu(op, memory_layout)

        elif isinstance(op, Elu):
            kernels += elu(op, memory_layout)

        elif isinstance(op, Sigmoid):
            kernels += sigmoid(op, memory_layout)

        elif isinstance(op, Tanh):
            kernels += tanh(op, memory_layout)

        elif isinstance(op, LocalResponseNormalization):
            kernels += local_response_normalization(op, memory_layout)

        elif isinstance(op, MaxPooling2D):
            kernels += max_pooling_2d(op, memory_layout)

        elif isinstance(op, AveragePooling2D):
            kernels += average_pooling_2d(op, memory_layout)

        elif isinstance(op, AxiswiseScale):
            kernels += axiswise_scale(op, memory_layout)

        elif isinstance(op, ElementwiseSum):
            kernels += elementwise_sum(op, memory_layout)

        elif isinstance(op, Flatten):
            kernels += flatten(op, memory_layout)

        elif isinstance(op, Sgemm):
            kernels += sgemm(op, memory_layout)

        elif isinstance(op, Im2Col):
            kernels += im2col(op, memory_layout)

        elif isinstance(op, Col2Im):
            kernels += col2im(op, memory_layout)

        elif isinstance(op, ScalarAffine):
            kernels += scalar_affine(op, memory_layout)

        elif isinstance(op, Concat):
            kernels += concat(op, memory_layout)

        elif isinstance(op, Embedding):
            kernels += embedding(op, memory_layout)

        elif isinstance(op, LSTM):
            kernels += lstm(op, memory_layout)

        elif isinstance(op, Operator):
            if "custom_kernel" in op.parameters:
                kernels += op.parameters["custom_kernel"](op, memory_layout)
                continue

            raise NotImplementedError(f"{op} is Unknown for WebassemblyDescriptorGenerator")

        else:
            raise NotImplementedError(f"{op} is Unknown for WebassemblyDescriptorGenerator")

    return kernels
