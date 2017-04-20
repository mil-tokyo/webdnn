#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import os.path as path

import numpy as np

from graph_builder.backend.fallback.generator import generate as generate_fallback_descriptor
from graph_builder.backend.webgpu.generator import generate as generate_webgpu_descriptor
from graph_builder.frontend.general_optimizer import GeneralOptimizer
from graph_builder.graph import Variable, operators as O
from graph_builder.graph.operators import attributes as A
from graph_builder.graph.variables import attributes as VA, Constant
from graph_builder.util import json

OUTPUT_DIR = path.join(path.dirname(__file__), "./output")


def main():
    x = Variable([1, 3], VA.OrderNC)

    h, = O.Linear("fc1")(x, Constant(np.array([[2, 3], [5, 7], [1.1, -1.3]], dtype=np.float32), VA.OrderCN))
    h, = O.AxiswiseBias("bias1", {"axis": A.Axis.C})(h, Constant(np.array([1.0, -10.0], dtype=np.float32), VA.OrderC))
    y, = O.Relu("relu1")(h)

    graph = O.Compose.compose_with_vars("graph", [x], [y])
    graph = GeneralOptimizer().optimize(graph)

    builder_type = "webgpu"
    if builder_type == "webgpu":
        descriptor, data = generate_webgpu_descriptor(graph)

    elif builder_type == "fallback":
        descriptor, data = generate_fallback_descriptor(graph)

    else:
        raise NotImplementedError()

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(path.join(OUTPUT_DIR, "graph_{}.json".format(builder_type)), "w") as f:
        json.dump(descriptor, f, indent=2)

    if builder_type == "webgpu":
        with open(path.join(OUTPUT_DIR, "kernels_{}.metal".format(builder_type)), "w") as f:
            f.write(descriptor.concat_kernel_sources())

    data.tofile(path.join(OUTPUT_DIR, "weight_{}.bin".format(builder_type)))


if __name__ == "__main__":
    main()
