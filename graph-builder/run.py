#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import os
import numpy as np
import json
from dnn_graph import DNNLayer, DNNLayerAttributes, DNNLayerType, DNNVariable, DNNGraphNode, DNNGraph, DNNVariableAttributes, DNNGraphOptimizer
from dnn_kernel_builder_webgpu import DNNKernelBuilderWebGPU, DNNDescriptorWebGPU

def main():
#     layer_l1_mul = DNNLayer('l1', DNNLayerType.Linear, set(), {'in_size': 3, 'out_size': 2}, {'W': np.array([[2, 3], [5, 7], [1.1, -1.3]], dtype=np.float32)}, [], None)
# #    layer_l1_bias = DNNLayer(DNNLayerType.Bias, {}, {'b': np.random.rand(2)}, [], [])
#     layer_relu = DNNLayer('relu', DNNLayerType.Relu, set(), {'out_size': 2}, {}, [], None)
#     var_x = DNNVariable('x', (1, 3), {DNNVariableAttributes.Input})
#     var_h = DNNVariable('h', (1, 2), set())
#     var_y = DNNVariable('y', (1, 2), {DNNVariableAttributes.Output})
#     node_l1_mul = DNNGraphNode(layer_l1_mul.name, layer_l1_mul, [var_x], [var_h])
#     node_relu = DNNGraphNode(layer_relu.name, layer_relu, [var_h], [var_y])
#     graph = DNNGraph([node_l1_mul, node_relu], [var_x], [var_y])
    layer_l0_mul = DNNLayer('l0', DNNLayerType.Linear, set(), {'in_size': 4, 'out_size': 3}, {'W': np.random.rand(4, 3).astype(np.float32)}, [], None)
    layer_l1_mul = DNNLayer('l1', DNNLayerType.Linear, set(), {'in_size': 3, 'out_size': 2}, {'W': np.array([[2, 3], [5, 7], [1.1, -1.3]], dtype=np.float32)}, [], None)
    layer_relu1 = DNNLayer('relu1', DNNLayerType.Relu, {DNNLayerAttributes.Elementwise}, {'out_size': 2}, {}, [], None)
    layer_relu2 = DNNLayer('relu2', DNNLayerType.Relu, set(), {'out_size': 2}, {}, [], None)
    var_x = DNNVariable('x', (1, 4), {DNNVariableAttributes.Input})
    var_x2 = DNNVariable('x2', (1, 3), set())
    var_h1 = DNNVariable('h1', (1, 2), set())
    var_h2 = DNNVariable('h2', (1, 2), set())
    var_y = DNNVariable('y', (1, 2), {DNNVariableAttributes.Output})
    node_l0_mul = DNNGraphNode(layer_l0_mul.name, layer_l0_mul, [var_x], [var_x2])
    node_l1_mul = DNNGraphNode(layer_l1_mul.name, layer_l1_mul, [var_x2], [var_h1])
    node_relu1 = DNNGraphNode(layer_relu1.name, layer_relu1, [var_h1], [var_h2])
    node_relu2 = DNNGraphNode(layer_relu2.name, layer_relu2, [var_h2], [var_y])
    graph = DNNGraph([node_l0_mul, node_l1_mul, node_relu1, node_relu2], [var_x], [var_y])
    optimizer = DNNGraphOptimizer(graph)
    optimizer.optimize()

    builder = DNNKernelBuilderWebGPU(graph, 1)
    builder.build()
    desc = builder.description
    desc_str = json.dumps(desc, indent=2)
    print(desc_str)
    with open('graph.json', 'w') as f:
        json.dump(desc, f, indent=2)
    builder.weight_array.tofile('weight.bin')

if __name__ == '__main__':
    main()
