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

from webdnn.backend.code_generator.allocator import allocate
from webdnn.backend.interface.generator import DescriptorGenerator
from webdnn.backend.interface.graph_descriptor import IGraphExecutionData
from webdnn.backend.webassembly.graph_descriptor import GraphDescriptor
from webdnn.backend.webassembly.kernel import Kernel
from webdnn.backend.webassembly.optimize_rules.webassembly_optimize_rule import WebassemblyOptimizeRule
from webdnn.encoder.constant_encoder import ConstantEncoder
from webdnn.graph import traverse
from webdnn.graph.graph import Graph
from webdnn.util import flags, console
from webdnn.util import json


class GraphExecutionData(IGraphExecutionData):
    descriptor: GraphDescriptor

    def __init__(self, graph: Graph, descriptor: GraphDescriptor, constants: bytes):
        self.graph = graph
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
        args.append(
            "EXPORTED_FUNCTIONS=['_run','_init','_get_static_buffer','_allocate_dynamic_buffer','_get_dynamic_buffer','_set_placeholder_value']")
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
        args.append(
            "EXPORTED_FUNCTIONS=['_run','_init','_get_static_buffer','_allocate_dynamic_buffer','_get_dynamic_buffer','_set_placeholder_value']")
        args.append("-s")
        args.append("WASM=0")
        args.append("-s")
        args.append(f"TOTAL_MEMORY={self.descriptor.required_heap}")
        args.append("-s")
        args.append(f"LEGACY_VM_SUPPORT=1")  # polyfills Math.imul, which is needed in IE11 (since emscripten v1.37.23)
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

        memory_layout = allocate(graph)

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

        return GraphExecutionData(graph, descriptor, constants_bytes)


def generate(graph: Graph, **kwargs):
    return WebassemblyDescriptorGenerator.generate(graph, **kwargs)
