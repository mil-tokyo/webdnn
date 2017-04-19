from os import path

import numpy as np

from graph_builder.graph import operators as O
from graph_builder.graph.graph import Variable
from graph_builder.graph.operators import attributes as A
from graph_builder.graph.variables import Constant
from graph_builder.optimizer import Optimizer

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

x = Variable([15, 784])
h, = O.Linear("l1", {"out_size": 100})(x, Constant(weights["l1/W"]))
h, = O.ChannelwiseBias("l1b")(h, Constant(weights["l1/b"]))
h, = O.Relu("l1r")(h)

h, = O.Linear("l2", {"out_size": 100})(h, Constant(weights["l2/W"]))
h, = O.ChannelwiseBias("l2b")(h, Constant(weights["l2/b"]))
h, = O.Relu("l2r")(h)

h, = O.Linear("l3", {"out_size": 50})(h, Constant(weights["l3/W"]))
y, = O.ChannelwiseBias("l3b")(h, Constant(weights["l3/b"]))

# graph = O.Compose.compose_with_vars("graph", [x], [y])
x.dump()

optimizer = Optimizer()

while True:
    for op in x.input_to:
        ma1 = optimizer.search_sub_structure(op, [A.PostChannelwise, A.Channelwise])
        ma2 = optimizer.search_sub_structure(op, [A.PostElementwise, A.Elementwise])

        if len(ma1) == 0 and len(ma2) == 0:
            exit()

        if len(ma1) > 0:
            composite = O.Compose.compose_ops(f"{ma1[0][0].name}_{ma1[0][1].name}", ma1[0])
            if A.Channelwise not in ma1[0][0].attributes:
                composite.attributes.remove(A.Channelwise)

            print()
            print()
            print()
            print()
            x.dump()

        if len(ma2) > 0:
            composite = O.Compose.compose_ops(f"{ma2[0][0].name}_{ma2[0][1].name}", ma2[0])
            if A.Elementwise not in ma2[0][0].attributes:
                composite.attributes.remove(A.Elementwise)

            print()
            print()
            print()
            print()
            x.dump()
