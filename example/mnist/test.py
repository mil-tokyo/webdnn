from os import path

import numpy as np

from graph_builder.backend.webgpu.generate import generate
from graph_builder.frontend.general_optimizer import GeneralOptimizer
from graph_builder.graph import operators as O
from graph_builder.graph.graph import Variable
from graph_builder.graph.operators import attributes as A
from graph_builder.graph.variables import Constant, attributes as VA
from graph_builder.util.json import json

RESOURCES_DIR = path.join(path.dirname(__file__), "../../resources/mnist")


def convert_fc_weight(buffers, weight_prefix, layer_name):
    w = buffers[weight_prefix + layer_name + "/W"]  # (out_ch, in_ch)
    b = buffers[weight_prefix + layer_name + "/b"]  # (out_ch, )
    return {layer_name + "/W": w.T, layer_name + "/b": b}


def load_mnist_weights_fc(path):
    snapshot_buffers = np.load(path)
    weight_prefix = "updater/model:main/predictor/"
    weights = {}
    weights.update(convert_fc_weight(snapshot_buffers, weight_prefix, "l1"))
    weights.update(convert_fc_weight(snapshot_buffers, weight_prefix, "l2"))
    weights.update(convert_fc_weight(snapshot_buffers, weight_prefix, "l3"))
    return weights


weights = load_mnist_weights_fc(path.join(RESOURCES_DIR, "snapshot_iter_12000"))

# ---------------------------------------------------------------------------------------------------------------------
# main

x = Variable([15, 784], axis_order=VA.OrderNC)
h, = O.Linear("l1", {"out_size": 100})(x, Constant(weights["l1/W"], VA.OrderCN))
h, = O.AxiswiseBias("l1b", {"axis": A.Axis.C})(h, Constant(weights["l1/b"], VA.OrderC))
h, = O.Relu("l1r")(h)

h, = O.Linear("l2", {"out_size": 100})(h, Constant(weights["l2/W"], VA.OrderCN))
h, = O.AxiswiseBias("l2b", {"axis": A.Axis.C})(h, Constant(weights["l2/b"], VA.OrderC))
h, = O.Relu("l2r")(h)

h, = O.Linear("l3", {"out_size": 50})(h, Constant(weights["l3/W"], VA.OrderCN))
y, = O.AxiswiseBias("l3b", {"axis": A.Axis.C})(h, Constant(weights["l3/b"], VA.OrderC))

graph = O.Compose.compose_with_vars("graph", [x], [y])
graph = GeneralOptimizer().optimize(graph)

descriptor, data = generate(graph)

with open("./output/graph_webgpu.json", "w+") as f:
    json.dump(descriptor, f, indent=4)

with open("./output/graph_webgpu.metal", "w+") as f:
    f.write(descriptor.concat_kernel_sources())

data.tofile(path.join("./output/weight_webgpu.bin"))
