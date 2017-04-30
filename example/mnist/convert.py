import argparse
import os
import os.path as path
from typing import Dict

import numpy as np

from graph_builder.backend.fallback.generator import generate as generate_fallback_descriptor
from graph_builder.backend.webgpu.generator import generate as generate_webgpu_descriptor
from graph_builder.frontend.general_optimize_rule import GeneralOptimizeRule
from graph_builder.graph.axis import Axis
from graph_builder.graph.graph import Graph
from graph_builder.graph.operators.axiswise_bias import AxiswiseBias
from graph_builder.graph.operators.convolution2d import Convolution2D
from graph_builder.graph.operators.linear import Linear
from graph_builder.graph.operators.relu import Relu
from graph_builder.graph.variable import Variable
from graph_builder.graph.variables.attributes.order import OrderNC, OrderCN, OrderC, OrderNHWC, OrderHWCN
from graph_builder.graph.variables.constant_variable import ConstantVariable
from graph_builder.util.json import json

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


def load_mnist_weights_fc(filepath: str):
    snapshot_buffers = np.load(filepath)
    weight_prefix = "updater/model:main/predictor/"
    weights = {}
    weights.update(convert_fc_weight(snapshot_buffers, weight_prefix, "l1"))
    weights.update(convert_fc_weight(snapshot_buffers, weight_prefix, "l2"))
    weights.update(convert_fc_weight(snapshot_buffers, weight_prefix, "l3"))
    return weights


def load_mnist_weights_conv(filepath: str):
    snapshot_buffers = np.load(filepath)
    weight_prefix = "updater/model:main/predictor/"
    weights = {}
    weights.update(convert_fc_weight(snapshot_buffers, weight_prefix, "conv1"))
    weights.update(convert_fc_weight(snapshot_buffers, weight_prefix, "conv2"))
    weights.update(convert_fc_weight(snapshot_buffers, weight_prefix, "conv3"))
    return weights


def construct_graph_fc(weights: np.array, batch_size: int = 1):
    x: Variable = Variable([batch_size, 784], axis_order=OrderNC)
    h, = Linear("fc1")(x, ConstantVariable(weights["l1/W"], OrderCN))
    h, = AxiswiseBias("bias1", {"axis": Axis.C})(h, ConstantVariable(weights["l1/b"], OrderC))
    h, = Relu("relu1")(h)

    h, = Linear("fc2")(h, ConstantVariable(weights["l2/W"], OrderCN))
    h, = AxiswiseBias("bias2", {"axis": Axis.C})(h, ConstantVariable(weights["l2/b"], OrderC))
    h, = Relu("relu2")(h)

    h, = Linear("fc3")(h, ConstantVariable(weights["l3/W"], OrderCN))
    y, = AxiswiseBias("bias3", {"axis": Axis.C})(h, ConstantVariable(weights["l3/b"], OrderC))

    return Graph([x], [y])


def construct_graph_conv(weights: Dict[str, np.array], batch_size: int = 1):
    x: Variable = Variable([batch_size, 28, 28, 1], axis_order=OrderNHWC)

    conv1 = Convolution2D("conv1", {"ksize": (5, 5), "stride": (1, 1), "padding": (0, 0)})
    h, = conv1(x, ConstantVariable(weights["conv1/W"], OrderHWCN))
    h, = AxiswiseBias("bias1", {"axis": Axis.C})(h, ConstantVariable(weights["conv1/b"], OrderC))
    h, = Relu("relu1")(h)

    conv2 = Convolution2D("conv2", {"ksize": (3, 3), "stride": (2, 2), "padding": (1, 1)})
    h, = conv2(h, ConstantVariable(weights["conv2/W"], OrderHWCN))
    h, = AxiswiseBias("bias2", {"axis": Axis.C})(h, ConstantVariable(weights["conv2/b"], OrderC))
    h, = Relu("relu2")(h)

    conv2 = Convolution2D("conv3", {"ksize": (12, 12), "stride": (1, 1), "padding": (0, 0)})
    h, = conv2(h, ConstantVariable(weights["conv3/W"], OrderHWCN))
    y, = AxiswiseBias("bias3", {"axis": Axis.C})(h, ConstantVariable(weights["conv3/b"], OrderC))

    return Graph([x], [y])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("nn_type", choices=["fc", "conv"])
    parser.add_argument("--backend", default="webgpu", choices=["webgpu", "fallback"])
    parser.add_argument("--optimize", action="store_true")
    args = parser.parse_args()

    if args.nn_type == "fc":
        weights = load_mnist_weights_fc(path.join(RESOURCES_DIR, "snapshot_iter_12000"))
        graph = construct_graph_fc(weights, batch_size=1)

    elif args.nn_type == "conv":
        weights = load_mnist_weights_conv(path.join(RESOURCES_DIR, "snapshot_conv"))
        graph = construct_graph_conv(weights, batch_size=1)

    else:
        raise NotImplementedError()

    if args.optimize:
        graph, _ = GeneralOptimizeRule().optimize(graph)

    if args.backend == "webgpu":
        descriptor, data = generate_webgpu_descriptor(graph)

    elif args.backend == "fallback":
        descriptor, data = generate_fallback_descriptor(graph)

    else:
        raise NotImplementedError()

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(path.join(OUTPUT_DIR, "graph_{}.json".format(args.backend)), "w") as f:
        json.dump(descriptor, f, indent=2)

    if args.backend == "webgpu":
        with open(path.join(OUTPUT_DIR, "kernels_{}.metal".format(args.backend)), "w") as f:
            f.write(descriptor.concat_kernel_sources())

    data.tofile(path.join(OUTPUT_DIR, "weight_{}.bin".format(args.backend)))


if __name__ == "__main__":
    main()
