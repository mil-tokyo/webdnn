from typing import List

from graph_builder.backend.fallback.operators.channelwise_bias import ChannelwiseBias
from graph_builder.backend.fallback.operators.linear import Linear
from graph_builder.backend.fallback.operators.operator import Operator
from graph_builder.backend.fallback.operators.relu import Relu
from graph_builder.backend.fallback.operators.convolution_2d import Convolution2D
from graph_builder.frontend.graph import Operator, OperatorType, Graph, Variable


class OperatorBuilder:
    @classmethod
    def build_from_graph(cls, graph: Graph) -> List[Operator]:
        operators = []
        for node in graph.nodes:
            operators.append(OperatorBuilder.build_from_layer(node.layer, node.bottoms, node.tops))

        return operators

    @classmethod
    def build_from_layer(cls,
                         layer: Operator,
                         inputs: List[Variable],
                         outputs: List[Variable]) -> Operator:
        if layer.operator_type == OperatorType.Linear:
            operator = Linear(layer, inputs, outputs)

        elif layer.operator_type == OperatorType.ChannelwiseBias:
            operator = ChannelwiseBias(layer, inputs, outputs)

        elif layer.operator_type == OperatorType.Relu:
            operator = Relu(layer, inputs, outputs)

        elif layer.operator_type == OperatorType.Convolution2D:
            operator = Convolution2D(layer, inputs, outputs)

        else:
            raise NotImplementedError(f"layer type: {layer.operator_type}")

        return operator
