#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import os.path as path
import numpy as np
from graph_builder.backend.webgpu.graph_descriptor_generator_webgpu import GraphDescriptorGeneratorWebGPU
from graph_builder.backend.fallback.graph_descriptor_generator_fallback import GraphDescriptorGeneratorFallback
from graph_builder.frontend.graph import LinearLayer, ChannelwiseBiasLayer, ReluLayer, Variable, GraphNode, Graph, VariableAttributes
from graph_builder.frontend.optimizer.graph_optimizer import GraphOptimizer
from graph_builder.util import json

OPTIMIZE = os.environ.get('OPTIMIZE', '1') == '1'
OUTPUT_DIR = path.join(path.dirname(__file__), "./output")
RESOURCES_DIR = path.join(path.dirname(__file__), "../../resources/mnist")


def convert_fc_weight(buffers, weight_prefix, layer_name):
    w = buffers[weight_prefix + layer_name + "/W"]  # (out_ch, in_ch)
    # transposition is needed (in_ch, out_ch)
    b = buffers[weight_prefix + layer_name + "/b"]  # (out_ch, )
    return {layer_name + "/W": w.T, layer_name + "/b": b}

def convert_conv_weight(buffers, weight_prefix, layer_name):
    w = buffers[weight_prefix + layer_name + "/W"]  # (out_ch, in_ch, kh, kw)
    w_trans = np.transpose(w, (2, 3, 1, 0))  # (kh, kw, in_ch, out_ch)
    b = buffers[weight_prefix + layer_name + "/b"]  # (out_ch, )
    return {layer_name + "/W": w_trans, layer_name + "/b": b}

def make_sequential_graph(layers, var_shapes, in_var_name, out_var_name, batch_size):
    nn_vars = []
    for i, var_shape in enumerate(var_shapes):
        name = "h_" + str(i)
        attrs = set()
        if i == 0:
            name = in_var_name
            attrs.add(VariableAttributes.Input)
        elif i == len(var_shapes) - 1:
            name = out_var_name
            attrs.add(VariableAttributes.Output)
        nn_vars.append(Variable(name, var_shape, attrs))

    nodes = []
    for i, layer in enumerate(layers):
        nodes.append(GraphNode(layer.name, layer, [nn_vars[i]], [nn_vars[i + 1]]))

    graph = Graph(nodes, [nn_vars[0]], [nn_vars[-1]], batch_size)
    return graph


def construct_graph(weights, batch_size):
    var_shapes = []
    layers = []
    var_shapes.append((batch_size, 784))
    layers.append(LinearLayer("l1", {"in_size": 784, "out_size": 100},
                              {"W": weights["l1/W"]}))
    var_shapes.append((batch_size, 100))
    layers.append(ChannelwiseBiasLayer("bias1", {"out_size": 100},
                                       {"b": weights["l1/b"]}))
    var_shapes.append((batch_size, 100))
    layers.append(ReluLayer("relu1", {"out_size": 100}))
    var_shapes.append((batch_size, 100))

    layers.append(LinearLayer("l2", {"in_size": 100, "out_size": 100},
                              {"W": weights["l2/W"]}))
    var_shapes.append((batch_size, 100))
    layers.append(ChannelwiseBiasLayer("bias2", {"out_size": 100},
                                       {"b": weights["l2/b"]}))
    var_shapes.append((batch_size, 100))
    layers.append(ReluLayer("relu2", {"out_size": 100}))
    var_shapes.append((batch_size, 100))

    layers.append(LinearLayer("l3", {"in_size": 100, "out_size": 10},
                              {"W": weights["l3/W"]}))
    var_shapes.append((batch_size, 10))
    layers.append(ChannelwiseBiasLayer("bias3", {"out_size": 10},
                                       {"b": weights["l3/b"]}))
    var_shapes.append((batch_size, 10))

    return make_sequential_graph(layers, var_shapes, "x", "y", batch_size)


def load_mnist_weights(path):
    snapshot_buffers = np.load(path)
    weight_prefix = "updater/model:main/predictor/"
    weights = {}
    weights.update(convert_fc_weight(snapshot_buffers, weight_prefix, "l1"))
    weights.update(convert_fc_weight(snapshot_buffers, weight_prefix, "l2"))
    weights.update(convert_fc_weight(snapshot_buffers, weight_prefix, "l3"))
    return weights


def main():
    weights = load_mnist_weights(path.join(RESOURCES_DIR, "snapshot_iter_12000"))
    graph = construct_graph(weights, batch_size=1)

    if OPTIMIZE:
        optimizer = GraphOptimizer(graph)
        optimizer.optimize()

    builder_type = "webgpu"
    if builder_type == "webgpu":
        builder = GraphDescriptorGeneratorWebGPU(graph)
        descriptor = builder.generate()
    elif builder_type == "fallback":
        builder = GraphDescriptorGeneratorFallback(graph)
        descriptor = builder.generate()
    else:
        raise NotImplementedError()

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(path.join(OUTPUT_DIR, "graph_{}.json".format(builder_type)), "w") as f:
        json.dump(descriptor, f, indent=2)
    if builder_type == "webgpu":
        with open(path.join(OUTPUT_DIR, "kernels_{}.metal".format(builder_type)), "w") as f:
            f.write(descriptor.concat_kernel_sources())

    builder.weights_array.tofile(path.join(OUTPUT_DIR, "weight_{}.bin".format(builder_type)))


if __name__ == "__main__":
    main()
