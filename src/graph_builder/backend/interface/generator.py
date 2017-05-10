from typing import Optional

from graph_builder.backend.fallback.generator import generate as generate_fallback
from graph_builder.backend.interface.graph_descriptor import IGraphExecutionData
from graph_builder.backend.webassembly.generator import generate as generate_webassembly
from graph_builder.backend.webgpu.generator import generate as generate_webgpu
from graph_builder.frontend.general_optimize_rule import GeneralOptimizeRule
from graph_builder.graph.graph import Graph
from graph_builder.util import flags

# FIXME: ここでよい？

generators = {"webgpu": generate_webgpu,
              "webassembly": generate_webassembly,
              "fallback": generate_fallback}


def generate_descriptor(backend: str, graph: Graph, constant_encoder_name: Optional[str] = None) -> IGraphExecutionData:
    if backend not in generators:
        raise NotImplementedError()

    if flags.optimize.OPTIMIZE:
        graph, _ = GeneralOptimizeRule().optimize(graph)

    return generators[backend](graph, constant_encoder_name=constant_encoder_name)
