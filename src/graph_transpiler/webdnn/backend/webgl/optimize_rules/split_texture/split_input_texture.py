from webdnn.backend.webgl.optimize_rules.split_texture.check_texture_size import SplitTarget
from webdnn.graph.graph import Graph
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.optimizer.sub_rules.dump_graph import DumpGraph
from webdnn.util import flags


class SplitInputTexture(OptimizeRule):
    """
    Split input texture (Currently, simply raise NotImplementedError)
    """

    def optimize(self, graph: Graph):
        for v in graph.inputs:
            if not v.has_attribute(SplitTarget):
                continue

            if flags.DEBUG:
                DumpGraph().optimize(graph)

            raise NotImplementedError(f"Input Variable {v} is too large to handle in WebGL backend")

        return graph, False
