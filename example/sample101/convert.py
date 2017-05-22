#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import os.path as path

import numpy as np

from webdnn.backend.interface.generator import generate_descriptor
from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.operators.axiswise_bias import AxiswiseBias
from webdnn.graph.operators.linear import Linear
from webdnn.graph.operators.relu import Relu
from webdnn.graph.order import OrderCN, OrderC, OrderNC
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable

OUTPUT_DIR = path.join(path.dirname(__file__), "./output")


def main():
    x: Variable = Variable([1, 3], OrderNC)

    h, = Linear("fc1")(x, ConstantVariable(np.array([[2, 3], [5, 7], [1.1, -1.3]], dtype=np.float32), OrderCN))
    h, = AxiswiseBias("bias1", {"axis": Axis.C})(h, ConstantVariable(np.array([1.0, -10.0], dtype=np.float32), OrderC))
    y, = Relu("relu1")(h)

    graph = Graph([x], [y])

    builder_type = "webgpu"
    graph_exec_data = generate_descriptor(builder_type, graph)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    graph_exec_data.save(OUTPUT_DIR)

if __name__ == "__main__":
    main()
