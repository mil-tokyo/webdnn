from graph_builder.backend.fallback.generator import generate as generate_fallback
from graph_builder.backend.interface.graph_descriptor import IGraphExecutionData
from graph_builder.backend.webassembly.generator import generate as generate_webassembly
from graph_builder.backend.webgpu.generator import generate as generate_webgpu
from graph_builder.graph.graph import Graph

# FIXME: ここでよい？

generators = {"webgpu": generate_webgpu,
              "webassembly": generate_webassembly,
              "fallback": generate_fallback}


def generate_descriptor(backend: str, graph: Graph, constant_encoder_name: str = None) -> IGraphExecutionData:
    if backend not in generators:
        raise NotImplementedError()
    return generators[backend](graph, constant_encoder_name=constant_encoder_name)
