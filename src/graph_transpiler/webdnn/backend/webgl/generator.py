import os
import os.path as path

from webdnn.backend.code_generator.allocator import Allocator
from webdnn.backend.interface.generator import DescriptorGenerator
from webdnn.backend.interface.graph_descriptor import IGraphExecutionData
from webdnn.backend.webgl.graph_descriptor import GraphDescriptor
from webdnn.backend.webgl.kernel import Kernel
from webdnn.backend.webgl.optimize_rules.webgl_optimize_rule import WebGLOptimizeRule
from webdnn.encoder.constant_encoder import ConstantEncoder
from webdnn.graph import traverse
from webdnn.graph.graph import Graph
from webdnn.util import flags, console
from webdnn.util.json import json


class GraphExecutionData(IGraphExecutionData[Kernel]):
    descriptor: GraphDescriptor

    def __init__(self, graph: Graph, descriptor: GraphDescriptor, constants: bytes):
        self.graph = graph
        self.descriptor = descriptor
        self.constants = constants
        self.backend_suffix = "webgl"

    def save(self, dirname: str):
        os.makedirs(dirname, exist_ok=True)

        with open(path.join(dirname, "graph_{}.json".format(self.backend_suffix)), "w") as f:
            json.dump(self.descriptor, f, indent=2)

        with open(path.join(dirname, "weight_{}.bin".format(self.backend_suffix)), "wb") as f:
            f.write(self.constants)


class WebGLDescriptorGenerator(DescriptorGenerator[Kernel, GraphExecutionData]):
    @classmethod
    def generate(cls, graph: Graph, **kwargs):
        graph, _ = WebGLOptimizeRule().optimize(graph)
        if flags.DEBUG:
            traverse.dump(graph)
            with open("cg.dot", "w") as f:
                f.write(traverse.dump_dot(graph))

        memory_layout = Allocator.allocate(graph)
        console.debug(f"[WebGLDescriptorGenerator] memory_layout total size: {memory_layout.total_size * 4}[B]")
        console.debug(f"[WebGLDescriptorGenerator] memory_layout static size: {memory_layout.static_size * 4}[B]")
        console.debug(f"[WebGLDescriptorGenerator] memory_layout dynamic size: {memory_layout.dynamic_size * 4}[B]")

        constant_encoder = ConstantEncoder.get_encoder(kwargs.get("constant_encoder_name", None))
        constants_bytes = constant_encoder.encode(memory_layout)

        console.debug(f"[WebGLDescriptorGenerator] constants encoded size: {len(constants_bytes)}[B]")

        kernels = cls.generate_kernels(graph, memory_layout)

        descriptor = GraphDescriptor(
            kernels=kernels,
            memory_layout=memory_layout,
            inputs=graph.inputs,
            outputs=graph.outputs,
            constants_encoding=constant_encoder.name,
            licenses=graph.licenses
        )

        return GraphExecutionData(graph, descriptor, constants_bytes)


def generate(graph: Graph, **kwargs):
    return WebGLDescriptorGenerator.generate(graph, **kwargs)
