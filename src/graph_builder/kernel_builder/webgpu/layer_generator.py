from typing import List

from graph_builder.graph import Layer, LayerType
from graph_builder.kernel_builder.webgpu.operators.channelwise_bias import KBChannelwiseBiasLayer
from graph_builder.kernel_builder.webgpu.operators.layer import KBLayer
from graph_builder.kernel_builder.webgpu.operators.linear import KBLinearLayer
from graph_builder.kernel_builder.webgpu.operators.relu import KBReluLayer


class KBLayerGenerator:
    @classmethod
    def generate(cls, layer: Layer) -> KBLayer:
        layers = []  # type: List[KBLayer]
        for layer in layer.iterate_self_and_children():
            layers.append(cls._generate_single(layer))

        root_layer = layers.pop(0)
        root_layer.children = layers

        return root_layer

    # noinspection PyMethodMayBeStatic
    @classmethod
    def _generate_single(cls, layer: Layer) -> KBLayer:
        if layer.layer_type == LayerType.Linear:
            kb_layer = KBLinearLayer(layer)

        elif layer.layer_type == LayerType.ChannelwiseBias:
            kb_layer = KBChannelwiseBiasLayer(layer)

        elif layer.layer_type == LayerType.Relu:
            kb_layer = KBReluLayer(layer)

        else:
            raise ValueError("Unknown layer")

        return kb_layer
