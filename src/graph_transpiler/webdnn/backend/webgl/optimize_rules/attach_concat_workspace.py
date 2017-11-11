from typing import Tuple

from webdnn.backend.webgl.attributes.texture_shape import TextureShape
from webdnn.graph import traverse
from webdnn.graph.attribute import Attribute
from webdnn.graph.graph import Graph
from webdnn.graph.operators.concat import Concat
from webdnn.graph.optimize_rule import OptimizeRule


class ConcatWorkspaceAttached(Attribute[Concat]):
    def __init__(self, base: Concat):
        super(ConcatWorkspaceAttached, self).__init__(base)
        workspace = base.outputs["y"].copy()
        base.append_input("workspace", workspace)

    def update(self) -> bool:
        base = self.base  # type: Concat
        y = base.outputs["y"]
        workspace = base.inputs["workspace"]
        flag_changed = False

        if y.order != workspace.order:
            flag_changed = True
            workspace.change_order(base.outputs["y"].order)

        if TextureShape.get(y) != TextureShape.get(workspace):
            flag_changed = True
            width, height = TextureShape.get(y)
            TextureShape.set(workspace, height, width)

        return flag_changed


class AttachConcatWorkspace(OptimizeRule):
    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        flag_changed = False
        for concat in traverse.filter_nodes(traverse.listup_operators(graph), Concat):  # type: Concat
            if concat.has_attribute(ConcatWorkspaceAttached):
                attr = concat.get_attribute(ConcatWorkspaceAttached)[0]

            else:
                flag_changed = True
                attr = ConcatWorkspaceAttached(concat)
                concat.attributes.add(attr)

            flag_changed |= attr.update()

        return graph, flag_changed
