from typing import Optional
import copy

from graph_transpiler.backend.fallback.generator import generate as generate_fallback
from graph_transpiler.backend.interface.graph_descriptor import IGraphExecutionData
from graph_transpiler.backend.webassembly.generator import generate as generate_webassembly
from graph_transpiler.backend.webgpu.generator import generate as generate_webgpu
from graph_transpiler.frontend.general_optimize_rule import GeneralOptimizeRule
from graph_transpiler.graph.graph import Graph
from graph_transpiler.util import flags

# FIXME: ここでよい？

generators = {"webgpu": generate_webgpu,
              "webassembly": generate_webassembly,
              "fallback": generate_fallback}


def generate_descriptor(backend: str, graph: Graph, constant_encoder_name: Optional[str] = None) -> IGraphExecutionData:
    if backend not in generators:
        raise NotImplementedError()

    graph = copy.deepcopy(graph)  # FIXME: バックエンドごとの最適化でgraphが変わってしまうので入れてあるが、もっと良い方法があれば変更

    if flags.optimize.OPTIMIZE:
        graph, _ = GeneralOptimizeRule().optimize(graph)

    return generators[backend](graph, constant_encoder_name=constant_encoder_name)
