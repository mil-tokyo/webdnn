#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import os.path as path
import sys

sys.path.append(path.join(path.dirname(__file__), "../../src"))

import numpy as np

from graph_builder.backend.webgpu.graph_descriptor_generator_webgpu import GraphDescriptorGeneratorWebGPU
from graph_builder.backend.fallback.graph_descriptor_generator_fallback import GraphDescriptorGeneratorFallback
from graph_builder.frontend.optimizer.graph_optimizer import GraphOptimizer
from graph_builder.frontend.graph import LinearLayer, ChannelwiseBiasLayer, ReluLayer, \
    Variable, GraphNode, Graph, VariableAttributes
from graph_builder.util import json


OUTPUT_DIR = path.join(path.dirname(__file__), "./output")


def main():
    layer_l1_mul = LinearLayer("l1", {"in_size": 3, "out_size": 2},
                               {"W": np.array([[2, 3], [5, 7], [1.1, -1.3]], dtype=np.float32)})
    layer_bias1 = ChannelwiseBiasLayer("bias1", {"out_size": 2},
                                       {"b": np.array([1.0, -10.0], dtype=np.float32)})
    layer_relu1 = ReluLayer("relu1", {"out_size": 2})

    var_x = Variable("x", (1, 3), {VariableAttributes.Input})
    var_h1 = Variable("h1", (1, 2))
    var_h2 = Variable("h2", (1, 2))
    var_y = Variable("y", (1, 2), {VariableAttributes.Output})
    node_l1_mul = GraphNode(layer_l1_mul.name, layer_l1_mul, [var_x], [var_h1])
    node_bias1 = GraphNode(layer_bias1.name, layer_bias1, [var_h1], [var_h2])
    node_relu1 = GraphNode(layer_relu1.name, layer_relu1, [var_h2], [var_y])
    graph = Graph([node_l1_mul, node_bias1, node_relu1], [var_x], [var_y], 1)
    optimizer = GraphOptimizer(graph)
    optimizer.optimize()

    builder_type = "fallback"
    if builder_type == "webgpu":
        builder = GraphDescriptorGeneratorWebGPU(graph)
        descriptor = builder.generate()
    elif builder_type == "fallback":
        builder = GraphDescriptorGeneratorFallback(graph)
        descriptor = builder.generate()

    desc_str = json.dumps(descriptor, indent=2)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(path.join(OUTPUT_DIR, "graph.json"), "w") as f:
        json.dump(descriptor, f, indent=2)
    if builder_type == "webgpu":
        with open(path.join(OUTPUT_DIR, "kernels.metal"), "w") as f:
            f.write(descriptor.concat_kernel_sources())

    builder.params_array.tofile(path.join(OUTPUT_DIR, "weight.bin"))


if __name__ == "__main__":
    main()
