import argparse
import os
import os.path as path
from typing import Dict

import numpy as np

from graph_builder.backend.fallback.generator import generate as generate_fallback_descriptor
from graph_builder.backend.webgpu.generator import generate as generate_webgpu_descriptor
from graph_builder.frontend.general_optimizer import GeneralOptimizer
from graph_builder.graph import operators as O
from graph_builder.graph.graph import Variable
from graph_builder.graph.operators import attributes as A
from graph_builder.graph.variables import Constant, attributes as VA
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
    x = Variable([batch_size, 784], axis_order=VA.OrderNC)
    h, = O.Linear("fc1")(x, Constant(weights["l1/W"], VA.OrderCN))
    h, = O.AxiswiseBias("bias1", {"axis": A.Axis.C})(h, Constant(weights["l1/b"], VA.OrderC))
    h, = O.Relu("relu1")(h)

    h, = O.Linear("fc2")(h, Constant(weights["l2/W"], VA.OrderCN))
    h, = O.AxiswiseBias("bias2", {"axis": A.Axis.C})(h, Constant(weights["l2/b"], VA.OrderC))
    h, = O.Relu("relu2")(h)

    h, = O.Linear("fc3")(h, Constant(weights["l3/W"], VA.OrderCN))
    y, = O.AxiswiseBias("bias3", {"axis": A.Axis.C})(h, Constant(weights["l3/b"], VA.OrderC))

    graph = O.Compose.compose_with_vars("graph", [x], [y])
    return graph


def construct_graph_conv(weights: Dict[str, np.array], batch_size: int = 1):
    x = Variable([batch_size, 28, 28, 1], axis_order=VA.OrderNHWC)

    conv1 = O.Convolution2D("conv1", {"ksize": (5, 5), "stride": (1, 1), "padding": (0, 0)})
    h, = conv1(x, Constant(weights["conv1/W"], VA.OrderHWCN))
    h, = O.AxiswiseBias("bias1", {"axis": A.Axis.C})(h, Constant(weights["conv1/b"], VA.OrderC))
    h, = O.Relu("relu1")(h)

    conv2 = O.Convolution2D("conv2", {"ksize": (3, 3), "stride": (2, 2), "padding": (1, 1)})
    h, = conv2(h, Constant(weights["conv2/W"], VA.OrderHWCN))
    h, = O.AxiswiseBias("bias2", {"axis": A.Axis.C})(h, Constant(weights["conv2/b"], VA.OrderC))
    h, = O.Relu("relu2")(h)

    conv2 = O.Convolution2D("conv3", {"ksize": (12, 12), "stride": (1, 1), "padding": (0, 0)})
    h, = conv2(h, Constant(weights["conv3/W"], VA.OrderHWCN))
    y, = O.AxiswiseBias("bias3", {"axis": A.Axis.C})(h, Constant(weights["conv3/b"], VA.OrderC))

    graph = O.Compose.compose_with_vars("graph", [x], [y])
    return graph


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
        graph = GeneralOptimizer().optimize(graph)

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
