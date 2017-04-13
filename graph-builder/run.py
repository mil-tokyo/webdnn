#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import os
import numpy as np
import json
from dnn_graph import DNNLayer, DNNLinearLayer, DNNBiasLayer, DNNScaleLayer, DNNReluLayer, DNNLayerAttributes, DNNLayerType, DNNVariable, DNNGraphNode, DNNGraph, DNNVariableAttributes, DNNGraphOptimizer
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
    layer_l1_mul = DNNLinearLayer('l1', {'in_size': 3, 'out_size': 2},
    {'W': np.array([[2, 3], [5, 7], [1.1, -1.3]], dtype=np.float32)}, [])
    layer_bias1 = DNNBiasLayer('bias1', {'out_size': 2}, 
    {'b': np.array([1.0, -10.0], dtype=np.float32)}, [])
    layer_relu1 = DNNReluLayer('relu1', {'out_size': 2}, {}, [])
    
    var_x = DNNVariable('x', (1, 3), {DNNVariableAttributes.Input})
    var_h1 = DNNVariable('h1', (1, 2), set())
    var_h2 = DNNVariable('h2', (1, 2), set())
    var_y = DNNVariable('y', (1, 2), {DNNVariableAttributes.Output})
    node_l1_mul = DNNGraphNode(layer_l1_mul.name, layer_l1_mul, [var_x], [var_h1])
    node_bias1 = DNNGraphNode(layer_bias1.name, layer_bias1, [var_h1], [var_h2])
    node_relu1 = DNNGraphNode(layer_relu1.name, layer_relu1, [var_h2], [var_y])
    graph = DNNGraph([node_l1_mul, node_bias1, node_relu1], [var_x], [var_y])
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
