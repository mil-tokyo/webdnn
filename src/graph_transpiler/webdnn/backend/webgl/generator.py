import os
import os.path as path
from typing import List

from webdnn.backend.interface.generator import DescriptorGenerator
from webdnn.backend.interface.graph_descriptor import IGraphExecutionData
from webdnn.backend.webgl.allocator import allocate
from webdnn.backend.webgl.graph_descriptor import GraphDescriptor
from webdnn.backend.webgl.kernel import Kernel
from webdnn.backend.webgl.optimize_rules.webgl_optimize_rule import WebGLOptimizeRule
from webdnn.encoder.constant_encoder import ConstantEncoder
from webdnn.graph import traverse
from webdnn.graph.graph import Graph
from webdnn.graph.variables.constant_variable import ConstantVariable
from webdnn.util import flags
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

        memory_layout = allocate(graph)

        constants_map = {}
        for constant in traverse.filter_nodes(traverse.listup_nodes(graph), ConstantVariable):  # type: ConstantVariable
            constants_map[constant.name] = {
                "byte_offset": memory_layout[constant].offset * 4,
                "size": constant.size
            }

        constant_encoder = ConstantEncoder.get_encoder(kwargs.get("constant_encoder_name", None))
        constants_bytes = constant_encoder.encode(memory_layout)

        kernels = cls.generate_kernels(graph)

        descriptor = GraphDescriptor(
            kernels=kernels,
            memory_layout=memory_layout,
            inputs=graph.inputs,
            outputs=graph.outputs,
            constants_encoding=constant_encoder.name,
            constants_map=constants_map,
            licenses=graph.licenses
        )

        return GraphExecutionData(graph, descriptor, constants_bytes)

    # noinspection PyMethodOverriding
    @classmethod
    def generate_kernels(cls, graph: Graph) -> List[Kernel]:
        kernels = []  # Type: List[T_KERNEL]

        for op in traverse.listup_operators(graph):
            key = cls.serialize_operator_type(op)
            if key not in cls._handler_map[cls.__name__]:
                raise NotImplementedError(f"[{cls.__name__}] Operator {op} is not handled by any generator handler")

            kernels += cls._handler_map[cls.__name__][key](op)

        return kernels


def generate(graph: Graph, **kwargs):
    return WebGLDescriptorGenerator.generate(graph, **kwargs)
