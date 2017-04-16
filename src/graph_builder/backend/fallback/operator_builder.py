from typing import List

from graph_builder.backend.fallback.operators.channelwise_bias import ChannelwiseBias
from graph_builder.backend.fallback.operators.linear import Linear
from graph_builder.backend.fallback.operators.operator import Operator
from graph_builder.backend.fallback.operators.relu import Relu
from graph_builder.frontend.graph import Layer, LayerType, Graph, Variable


class OperatorBuilder:
    @classmethod
    def build_from_graph(cls, graph: Graph) -> List[Operator]:
        operators = []
        for node in graph.nodes:
            operators.append(OperatorBuilder.build_from_layer(node.layer, node.bottoms, node.tops))

        return operators

    @classmethod
    def build_from_layer(cls,
                         layer: Layer,
                         inputs: List[Variable],
                         outputs: List[Variable]) -> Operator:
        if layer.layer_type == LayerType.Linear:
            operator = Linear(layer, inputs, outputs)

        elif layer.layer_type == LayerType.ChannelwiseBias:
            operator = ChannelwiseBias(layer, inputs, outputs)

        elif layer.layer_type == LayerType.Relu:
            operator = Relu(layer, inputs, outputs)

        else:
            raise NotImplementedError(f"layer type: {layer.layer_type}")

        return operator
