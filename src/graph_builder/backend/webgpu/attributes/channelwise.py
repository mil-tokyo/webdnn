from abc import abstractmethod

from graph_builder.backend.webgpu.attributes.attribute import Attribute


class ChannelwiseAttribute(Attribute):
    @abstractmethod
    def apply_channelwise_operation(self, expression: str, channel_index: str) -> str:
        raise NotImplementedError
