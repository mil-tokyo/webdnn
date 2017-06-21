"""
Descriptor Generator for WebAssembly

- kernel source generation
- schedule memory allocation
"""

import os
import os.path as path
import platform
import subprocess
import sys

from webdnn.backend.code_generator.allocator import Allocator
from webdnn.backend.interface.generator import DescriptorGenerator
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
from webdnn.backend.webassembly.kernels.embedding import embedding
from webdnn.backend.webassembly.kernels.flatten import flatten
from webdnn.backend.webassembly.kernels.im2col import im2col
from webdnn.backend.webassembly.kernels.local_response_normalization import local_response_normalization
from webdnn.backend.webassembly.kernels.lstm import lstm
from webdnn.backend.webassembly.kernels.max_pooling_2d import max_pooling_2d
from webdnn.backend.webassembly.kernels.relu import relu
from webdnn.backend.webassembly.kernels.scalar_affine import scalar_affine
from webdnn.backend.webassembly.kernels.sgemm import sgemm
from webdnn.backend.webassembly.kernels.sigmoid import sigmoid
from webdnn.backend.webassembly.kernels.tanh import tanh
from webdnn.backend.webassembly.operators.col2im import Col2Im
from webdnn.backend.webassembly.operators.im2col import Im2Col
from webdnn.backend.webassembly.operators.sgemm import Sgemm
from webdnn.backend.webassembly.optimize_rules.webassembly_optimize_rule import WebassemblyOptimizeRule
from webdnn.encoder.constant_encoder import ConstantEncoder
from webdnn.graph import traverse
from webdnn.graph.graph import Graph
from webdnn.graph.operators.average_pooling_2d import AveragePooling2D
from webdnn.graph.operators.axiswise_bias import AxiswiseBias
from webdnn.graph.operators.axiswise_scale import AxiswiseScale
from webdnn.graph.operators.concat import Concat
from webdnn.graph.operators.elementwise_sum import ElementwiseSum
from webdnn.graph.operators.elu import Elu
from webdnn.graph.operators.embedding import Embedding
from webdnn.graph.operators.flatten import Flatten
from webdnn.graph.operators.local_response_normalization import LocalResponseNormalization
from webdnn.graph.operators.lstm import LSTM
from webdnn.graph.operators.max_pooling_2d import MaxPooling2D
from webdnn.graph.operators.relu import Relu
from webdnn.graph.operators.scalar_affine import ScalarAffine
from webdnn.graph.operators.sigmoid import Sigmoid
from webdnn.graph.operators.tanh import Tanh
from webdnn.util import flags, console
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
        args.append("EXPORTED_FUNCTIONS=['_run','_init','_get_static_buffer','_allocate_dynamic_buffer','_get_dynamic_buffer','_set_placeholder_value']")
        args.append("-s")
        args.append("WASM=1")
        args.append("-s")
        args.append(f"TOTAL_MEMORY={self.descriptor.required_heap}")
        args.append("-s")
        args.append(f"ALLOW_MEMORY_GROWTH=1")  # cannot be used in asm.js
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
        backend_suffix = "asmjs"
        # noinspection PyListCreation
        args = ["em++"]
        args.append(path.join(dirname, "kernels_{}.cpp".format(self.backend_suffix)))
        args.append("-O3")
        args.append("-std=c++11")
        args.append("-s")
        args.append("EXPORTED_FUNCTIONS=['_run','_init','_get_static_buffer','_allocate_dynamic_buffer','_get_dynamic_buffer','_set_placeholder_value']")
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


class WebassemblyDescriptorGenerator(DescriptorGenerator[Kernel, GraphExecutionData]):
    @classmethod
    def generate(cls, graph: Graph, **kwargs):
        graph, _ = WebassemblyOptimizeRule().optimize(graph)
        if flags.DEBUG:
            traverse.dump(graph)

        memory_layout = Allocator.allocate(graph)

        console.debug(f"[WebassemblyDescriptorGenerator] memory_layout total size: {memory_layout.total_size * 4}")
        console.debug(f"[WebassemblyDescriptorGenerator] memory_layout static size: {memory_layout.static_size * 4}")
        console.debug(f"[WebassemblyDescriptorGenerator] memory_layout dynamic size: {memory_layout.dynamic_size * 4}")

        constant_encoder = ConstantEncoder.get_encoder(kwargs.get("constant_encoder_name", None))
        constants_bytes = constant_encoder.encode(memory_layout)

        console.debug(f"[WebassemblyDescriptorGenerator] constants encoded size: {len(constants_bytes)}")

        kernels = cls.generate_kernels(graph, memory_layout)

        heap_block_size = 16 * 1024 * 1024
        if isinstance(memory_layout.dynamic_size, int):
            dynamic_size_byte_int = memory_layout.dynamic_size * 4
        else:
            dynamic_size_byte_int = kwargs.get("dynamic_allocation_size", heap_block_size)
        total_size_byte = memory_layout.static_size * 4 + dynamic_size_byte_int

        # required for calculation (size ceiling to one block) + one block
        required_heap = ((total_size_byte + heap_block_size - 1) // heap_block_size + 1) * heap_block_size

        descriptor = GraphDescriptor(
            kernels=kernels,
            memory_layout=memory_layout,
            inputs=graph.inputs,
            outputs=graph.outputs,
            constants_encoding=constant_encoder.name,
            required_heap=required_heap,
            licenses=graph.licenses)

        return GraphExecutionData(descriptor, constants_bytes)


def generate(graph: Graph, **kwargs):
    return WebassemblyDescriptorGenerator.generate(graph, **kwargs)


WebassemblyDescriptorGenerator.register_handler(AveragePooling2D)(average_pooling_2d)
WebassemblyDescriptorGenerator.register_handler(AxiswiseBias)(axiswise_bias)
WebassemblyDescriptorGenerator.register_handler(AxiswiseScale)(axiswise_scale)
WebassemblyDescriptorGenerator.register_handler(Col2Im)(col2im)
WebassemblyDescriptorGenerator.register_handler(Concat)(concat)
WebassemblyDescriptorGenerator.register_handler(ElementwiseSum)(elementwise_sum)
WebassemblyDescriptorGenerator.register_handler(Elu)(elu)
WebassemblyDescriptorGenerator.register_handler(Embedding)(embedding)
WebassemblyDescriptorGenerator.register_handler(Flatten)(flatten)
WebassemblyDescriptorGenerator.register_handler(Im2Col)(im2col)
WebassemblyDescriptorGenerator.register_handler(LocalResponseNormalization)(local_response_normalization)
WebassemblyDescriptorGenerator.register_handler(LSTM)(lstm)
WebassemblyDescriptorGenerator.register_handler(MaxPooling2D)(max_pooling_2d)
WebassemblyDescriptorGenerator.register_handler(Relu)(relu)
WebassemblyDescriptorGenerator.register_handler(ScalarAffine)(scalar_affine)
WebassemblyDescriptorGenerator.register_handler(Sigmoid)(sigmoid)
WebassemblyDescriptorGenerator.register_handler(Sgemm)(sgemm)
WebassemblyDescriptorGenerator.register_handler(Tanh)(tanh)
