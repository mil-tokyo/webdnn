from webdnn.backend.webgl.attributes.texture_shape import TextureShape
from webdnn.graph import traverse
from webdnn.graph.attribute import Attribute
from webdnn.graph.graph import Graph
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.placeholder import Placeholder
from webdnn.util import config


class SplitTarget(Attribute):
    pass


class CheckTextureSize(OptimizeRule):
    """
    - Find all variables whose texture size is larger than the threshold
        - If no variable is found, this optimization is not needed. Finish.

    - For each found variable, :code:`v`,
        - attach :code:`SplitTarget` attribute to :code:`v`.
        - attach :code:`SplitInput` attribute to all operators in :code:`v.input_to`.
        - attach :code:`SplitOutput` attribute to :code:`v.output_from`.
    """

    def optimize(self, graph: Graph):
        MAX_TEXTURE_SIZE = config.WEBGL_MAX_TEXTURE_SIZE
        flag_changed = False

        for v in traverse.listup_variables(graph):
            if not Placeholder.check_resolved(v.size):
                continue

            height, width = TextureShape.get(v)
            if height <= MAX_TEXTURE_SIZE and width <= MAX_TEXTURE_SIZE:
                continue

            if not v.has_attribute(SplitTarget):
                flag_changed = True
                v.attributes.add(SplitTarget())

        return graph, flag_changed
