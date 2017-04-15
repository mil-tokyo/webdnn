from graph_builder.backend.webgpu.attributes.elementwise import Elementwise
from graph_builder.backend.webgpu.attributes.attribute import Attribute
from graph_builder.backend.webgpu.tag_parser import TagParser


class ElementwiseAttachable(Attribute):
    def apply_elementwise_attach(self, source: str) -> str:
        for tag in TagParser.parse(source):
            if tag.name == "ELEMENTWISE_ATTACHABLE":
                expression = tag.args[0]

                # noinspection PyUnresolvedReferences
                for child in self.iter_children_all():
                    if isinstance(child, Elementwise):
                        expression = child.apply_elementwise_operation(expression)

                source = source[:tag.span[0]] + expression + source[tag.span[1]:]

        return source
