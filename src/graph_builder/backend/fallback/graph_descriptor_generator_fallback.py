# -*- coding:utf-8 -*-

"""
Kernel Builder for Fallback (pure js)

- kernel source generation
- schedule memory allocation
"""

import numpy as np

from graph_builder.backend.interface.kernel_builder import GraphDescriptorGenerator
from graph_builder.backend.fallback.allocator import Allocator
from graph_builder.backend.fallback.graph_descriptor_fallback import GraphDescriptorFallback
from graph_builder.backend.fallback.operator_builder import OperatorBuilder
from graph_builder.frontend.graph import Graph, Variable, GraphNode


class GraphDescriptorGeneratorFallback(GraphDescriptorGenerator):
    allocator: Allocator
    params_array: np.ndarray
    #  descriptor: GraphDescriptorFallback

    def __init__(self, graph: Graph):
        super().__init__(graph)
        self.params_array = None
        self.descriptor = None

    def generate(self) -> GraphDescriptorFallback:
        batch_size = self.graph.batch_size
        u_graph = self._unfold_layer_chain()
        params_layout, self.params_array = Allocator.allocate_params(u_graph)
        variable_layout = Allocator.allocate_variables(u_graph)
        operators = OperatorBuilder.build_from_graph(u_graph)

        kernels = []
        for operator in operators:
            kernels.extend(operator.convert_to_kernels(
                batch_size
            ))

        return GraphDescriptorFallback(
            kernels=kernels,
            params_layout=params_layout,
            variable_layout=variable_layout,
            inputs=self.graph.inputs,
            outputs=self.graph.outputs,
            batch_size=self.graph.batch_size
        )

    def _unfold_layer_chain(self):
        """
        レイヤーの連結を解除し、中間変数を足したグラフを作る
        :return: 
        """
        graph = self.graph
        u_nodes = []
        tmp_serial = 0
        for node in graph.nodes:
            layer = node.layer
            bottoms = node.bottoms
            while layer.next_node is not None:
                #  後続ノードとの受け渡し変数を作る
                assert len(node.tops) == 1
                tops = [Variable('tmp_' + str(tmp_serial), node.tops[0].shape)]
                u_nodes.append(GraphNode(node.name + '_unfold_' + str(tmp_serial), layer, bottoms, tops))
                tmp_serial += 1
                layer = layer.next_node
                bottoms = tops
            u_nodes.append(GraphNode('tmp_' + str(tmp_serial), layer, bottoms, node.tops))
            tmp_serial += 1
        u_graph = Graph(u_nodes, graph.inputs, outputs=graph.outputs, batch_size=graph.batch_size)
        return u_graph
