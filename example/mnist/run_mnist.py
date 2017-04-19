#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse
import os
import os.path as path

import numpy as np

from graph_builder.backend.fallback.graph_descriptor_generator_fallback import GraphDescriptorGeneratorFallback
from graph_builder.backend.webgpu.graph_descriptor_generator_webgpu import GraphDescriptorGeneratorWebGPU
from graph_builder.frontend.graph import LinearOperator, ChannelwiseBiasOperator, ReluOperator, Convolution2DOperator, \
    Variable, \
    VariableAttributes, CompositeOperator, ConstantVariable
from graph_builder.frontend.graph_optimizer import GraphOptimizer
from graph_builder.util import json

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

    ops = set()
    for i, layer in enumerate(layers):
        ops.add(GraphNode(layer.name, layer, [nn_vars[i]], [nn_vars[i + 1]]))

    return CompositeOperator("graph", ops)


def construct_graph_fc(weights, batch_size):
    x = Variable([batch_size, 784])

    h = LinearOperator("l1", {"out_size": 100})(x, ConstantVariable(weights["l1/W"]))
    h = ChannelwiseBiasOperator("l1b")(h, ConstantVariable(weights["l1/b"]))
    h = ReluOperator("l1r")(h)

    h = LinearOperator("l2", {"out_size": 100})(h, ConstantVariable(weights["l2/W"]))
    h = ChannelwiseBiasOperator("l2b")(h, ConstantVariable(weights["l2/b"]))
    h = ReluOperator("l2r")(h)

    h = LinearOperator("l3", {"out_size": 100})(h, ConstantVariable(weights["l3/W"]))
    y = ChannelwiseBiasOperator("l3b")(h, ConstantVariable(weights["l3/b"]))

    graph = CompositeOperator.compose_with_vars("graph", [x], [y])
    print(graph)
    return graph


def construct_graph_conv(weights, batch_size):
    var_shapes = []
    layers = []
    var_shapes.append((batch_size, 28, 28, 1))  # n, h, w, c
    layers.append(Convolution2DOperator("conv1",
                                        {"in_size": 1, "out_size": 32,
                                         "ksize": (5, 5), "stride": (1, 1), "pad": (0, 0), "cover_all": False},
                                        {"W": weights["conv1/W"]}))
    var_shapes.append((batch_size, 24, 24, 32))
    layers.append(ChannelwiseBiasOperator("bias1", {"out_size": 32},
                                          {"b": weights["conv1/b"]}))
    var_shapes.append((batch_size, 24, 24, 32))
    layers.append(ReluOperator("relu1", {"out_size": 32}))
    var_shapes.append((batch_size, 24, 24, 32))

    layers.append(Convolution2DOperator("conv2",
                                        {"in_size": 32, "out_size": 32,
                                         "ksize": (3, 3), "stride": (2, 2), "pad": (1, 1), "cover_all": False},
                                        {"W": weights["conv2/W"]}))
    var_shapes.append((batch_size, 12, 12, 32))
    layers.append(ChannelwiseBiasOperator("bias2", {"out_size": 32},
                                          {"b": weights["conv2/b"]}))
    var_shapes.append((batch_size, 12, 12, 32))
    layers.append(ReluOperator("relu2", {"out_size": 32}))
    var_shapes.append((batch_size, 12, 12, 32))

    layers.append(Convolution2DOperator("conv3",
                                        {"in_size": 32, "out_size": 10,
                                         "ksize": (12, 12), "stride": (1, 1), "pad": (0, 0), "cover_all": False},
                                        {"W": weights["conv3/W"]}))
    var_shapes.append((batch_size, 1, 1, 10))
    layers.append(ChannelwiseBiasOperator("bias3", {"out_size": 10},
                                          {"b": weights["conv3/b"]}))
    var_shapes.append((batch_size, 1, 1, 10))

    return make_sequential_graph(layers, var_shapes, "x", "y", batch_size)


def load_mnist_weights_fc(path):
    snapshot_buffers = np.load(path)
    weight_prefix = "updater/model:main/predictor/"
    weights = {}
    weights.update(convert_fc_weight(snapshot_buffers, weight_prefix, "l1"))
    weights.update(convert_fc_weight(snapshot_buffers, weight_prefix, "l2"))
    weights.update(convert_fc_weight(snapshot_buffers, weight_prefix, "l3"))
    return weights


def load_mnist_weights_conv(path):
    snapshot_buffers = np.load(path)
    weight_prefix = "updater/model:main/predictor/"
    weights = {}
    weights.update(convert_conv_weight(snapshot_buffers, weight_prefix, "conv1"))
    weights.update(convert_conv_weight(snapshot_buffers, weight_prefix, "conv2"))
    weights.update(convert_conv_weight(snapshot_buffers, weight_prefix, "conv3"))
    return weights


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("nn_type")
    parser.add_argument("--builder_type", default="webgpu")
    parser.add_argument("--optimize", action="store_true")
    args = parser.parse_args()
    if args.nn_type == "fc":
        weights = load_mnist_weights_fc(path.join(RESOURCES_DIR, "snapshot_iter_12000"))
        graph = construct_graph_fc(weights, batch_size=1)
    elif args.nn_type == "conv":
        weights = load_mnist_weights_conv(path.join(RESOURCES_DIR, "snapshot_conv"))
        graph = construct_graph_conv(weights, batch_size=1)

    if args.optimize:
        optimizer = GraphOptimizer(graph)
        optimizer.optimize()

    builder_type = args.builder_type
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
