#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import os
import numpy as np
import json
from dnn_graph import DNNLayer, DNNLinearLayer, DNNBiasLayer, DNNScaleLayer, DNNReluLayer, DNNLayerAttributes, DNNLayerType, DNNVariable, DNNGraphNode, DNNGraph, DNNVariableAttributes, DNNGraphOptimizer
from dnn_kernel_builder_webgpu import DNNKernelBuilderWebGPU, DNNDescriptorWebGPU


def convert_fc_weight(buffers, weight_prefix, layer_name):
    w = buffers[weight_prefix + layer_name + "/W"]#(out_ch, in_ch)
    # transposition is needed (in_ch, out_ch)
    b = buffers[weight_prefix + layer_name + "/b"]#(out_ch, )
    return {layer_name + "/W": w.T, layer_name + "/b": b}

def make_sequential_graph(layers, var_shapes, in_var_name, out_var_name, batch_size):
    nn_vars = []
    for i, var_shape in enumerate(var_shapes):
        name = 'h_' + str(i)
        attrs = set()
        if i == 0:
            name = in_var_name
            attrs.add(DNNVariableAttributes.Input)
        elif i == len(var_shapes) - 1:
            name = out_var_name
            attrs.add(DNNVariableAttributes.Output)
        nn_vars.append(DNNVariable(name, var_shape, attrs))
    
    nodes = []
    for i, layer in enumerate(layers):
        nodes.append(DNNGraphNode(layer.name, layer, [nn_vars[i]], [nn_vars[i+1]]))

    graph = DNNGraph(nodes, [nn_vars[0]], [nn_vars[-1]], batch_size)
    return graph

def construct_graph(weights, batch_size):
    var_shapes = []
    layers = []
    var_shapes.append((batch_size, 784))
    layers.append(DNNLinearLayer('l1', {'in_size': 784, 'out_size': 100},
    {'W': weights['l1/W']}))
    var_shapes.append((batch_size, 100))
    layers.append(DNNBiasLayer('bias1', {'out_size': 100},
    {'b': weights['l1/b']}))
    var_shapes.append((batch_size, 100))
    layers.append(DNNReluLayer('relu1', {'out_size': 100}))
    var_shapes.append((batch_size, 100))

    layers.append(DNNLinearLayer('l2', {'in_size': 100, 'out_size': 100},
    {'W': weights['l2/W']}))
    var_shapes.append((batch_size, 100))
    layers.append(DNNBiasLayer('bias2', {'out_size': 100},
    {'b': weights['l2/b']}))
    var_shapes.append((batch_size, 100))
    layers.append(DNNReluLayer('relu2', {'out_size': 100}))
    var_shapes.append((batch_size, 100))

    layers.append(DNNLinearLayer('l3', {'in_size': 100, 'out_size': 10},
    {'W': weights['l3/W']}))
    var_shapes.append((batch_size, 10))
    layers.append(DNNBiasLayer('bias3', {'out_size': 10},
    {'b': weights['l3/b']}))
    var_shapes.append((batch_size, 10))

    return make_sequential_graph(layers, var_shapes, 'x', 'y', batch_size)

def load_mnist_weights(path):
    snapshot_buffers = np.load(path)
    weight_prefix = "updater/model:main/predictor/"
    weights = {}
    weights.update(convert_fc_weight(snapshot_buffers, weight_prefix, "l1"))
    weights.update(convert_fc_weight(snapshot_buffers, weight_prefix, "l2"))
    weights.update(convert_fc_weight(snapshot_buffers, weight_prefix, "l3"))
    return weights

def main():
    weights = load_mnist_weights("result_unit100/snapshot_iter_12000")
    graph = construct_graph(weights, batch_size=1)

    optimizer = DNNGraphOptimizer(graph)
    optimizer.optimize()

    builder = DNNKernelBuilderWebGPU(graph)
    builder.build()
    desc = builder.description
    desc_str = json.dumps(desc, indent=2)
    print(desc_str)
    with open('graph.json', 'w') as f:
        json.dump(desc, f, indent=2)
    builder.weight_array.tofile('weight.bin')

if __name__ == '__main__':
    main()
