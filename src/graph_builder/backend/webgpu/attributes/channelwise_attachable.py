from graph_builder.backend.webgpu.attributes.attribute import Attribute
from graph_builder.backend.webgpu.attributes.channelwise import Channelwise
from graph_builder.backend.webgpu.tag_parser import TagParser


class ChannelwiseAttachable(Attribute):
    def apply_channelwise_attach(self, source: str) -> str:
        for tag in TagParser.parse(source):
            if tag.name == "CHANNELWISE_ATTACHABLE":
                expression = tag.args[0]
                channel_index = tag.args[1]

                # noinspection PyUnresolvedReferences
                for child in self.iter_children_all():
                    if isinstance(child, Channelwise):
                        expression = child.apply_channelwise_operation(expression, channel_index)

                source = source[:tag.span[0]] + expression + source[tag.span[1]:]

        return source
