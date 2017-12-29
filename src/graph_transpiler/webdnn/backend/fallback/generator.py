# -*- coding:utf-8 -*-

"""
Kernel Builder for Fallback (pure js)

- kernel source generation
- schedule memory allocation
"""
import os
import os.path as path

from webdnn.backend.code_generator.allocator import allocate
from webdnn.backend.fallback.graph_descriptor import GraphDescriptor
from webdnn.backend.fallback.kernel import Kernel
from webdnn.backend.interface.generator import DescriptorGenerator
from webdnn.backend.interface.graph_descriptor import IGraphExecutionData
from webdnn.encoder.constant_encoder import ConstantEncoder
from webdnn.graph import traverse
from webdnn.graph.graph import Graph
from webdnn.util import console, flags
from webdnn.util import json


class GraphExecutionData(IGraphExecutionData):
    descriptor: GraphDescriptor

    def __init__(self, graph: Graph, descriptor: GraphDescriptor, constants: bytes):
        self.graph = graph
        self.descriptor = descriptor
        self.constants = constants
        self.backend_suffix = "fallback"

    def save(self, dirname: str):
        os.makedirs(dirname, exist_ok=True)

        with open(path.join(dirname, "graph_{}.json".format(self.backend_suffix)), "w") as f:
            json.dump(self.descriptor, f, indent=2)

        with open(path.join(dirname, "kernels_{}.js".format(self.backend_suffix)), "w") as f:
            f.write(self.descriptor.concat_kernel_sources())

        with open(path.join(dirname, "weight_{}.bin".format(self.backend_suffix)), "wb") as f:
            f.write(self.constants)


class FallbackDescriptorGenerator(DescriptorGenerator[Kernel, GraphExecutionData]):
    @classmethod
    def generate(cls, graph: Graph, **kwargs):
        if flags.DEBUG:
            traverse.dump(graph)

        memory_layout = allocate(graph)

        console.debug(f"[FallbackDescriptorGenerator] memory_layout total size: {memory_layout.total_size * 4}")
        console.debug(f"[FallbackDescriptorGenerator] memory_layout static size: {memory_layout.static_size * 4}")
        console.debug(f"[FallbackDescriptorGenerator] memory_layout dynamic size: {memory_layout.dynamic_size * 4}")

        constant_encoder = ConstantEncoder.get_encoder(kwargs.get("constant_encoder_name", None))
        constants_bytes = constant_encoder.encode(memory_layout)

        console.debug(f"[FallbackDescriptorGenerator] constants encoded size: {len(constants_bytes)}")

        descriptor = GraphDescriptor(
            kernels=cls.generate_kernels(graph, memory_layout),
            memory_layout=memory_layout,
            inputs=graph.inputs,
            outputs=graph.outputs,
            constants_encoding=constant_encoder.name,
            licenses=graph.licenses)

        return GraphExecutionData(graph, descriptor, constants_bytes)


def generate(graph: Graph, **kwargs):
    return FallbackDescriptorGenerator.generate(graph, **kwargs)
