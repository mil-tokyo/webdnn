import argparse
import os
import os.path as path
from typing import Dict

import numpy as np

from graph_transpiler.backend.interface.generator import generate_descriptor
from graph_transpiler.frontend.general_optimize_rule import GeneralOptimizeRule
from graph_transpiler.graph.axis import Axis
from graph_transpiler.graph.graph import Graph
from graph_transpiler.graph.operators.axiswise_bias import AxiswiseBias
from graph_transpiler.graph.operators.convolution2d import Convolution2D
from graph_transpiler.graph.operators.linear import Linear
from graph_transpiler.graph.operators.relu import Relu
from graph_transpiler.graph.variable import Variable
from graph_transpiler.graph.variables.attributes.order import OrderNC, OrderCN, OrderC, OrderNHWC, OrderHWNC
from graph_transpiler.graph.variables.constant_variable import ConstantVariable

OUTPUT_DIR = path.join(path.dirname(__file__), "./output")
RESOURCES_DIR = path.join(path.dirname(__file__), "../../resources/mnist")


def convert_fc_weight(buffers, weight_prefix, layer_name):
    w = buffers[weight_prefix + layer_name + "/W"]  # (out_ch, in_ch)
    # transposition is needed (in_ch, out_ch)
    b = buffers[weight_prefix + layer_name + "/b"]  # (out_ch, )
    return {layer_name + "/W": w.T, layer_name + "/b": b}


def convert_conv_weight(buffers, weight_prefix, layer_name):
    w = buffers[weight_prefix + layer_name + "/W"]  # (out_ch, in_ch, kh, kw)
    w_trans = np.transpose(w, (2, 3, 0, 1))  # (kh, kw, out_ch, in_ch)
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
    weights.update(convert_conv_weight(snapshot_buffers, weight_prefix, "conv1"))
    weights.update(convert_conv_weight(snapshot_buffers, weight_prefix, "conv2"))
    weights.update(convert_conv_weight(snapshot_buffers, weight_prefix, "conv3"))
    return weights


def construct_graph_fc(weights: np.array, batch_size: int = 1) -> Graph:
    x = Variable([batch_size, 784], order=OrderNC)
    h, = Linear(None)(x, ConstantVariable(weights["l1/W"], OrderCN))
    h, = AxiswiseBias(None, axis=Axis.C)(h, ConstantVariable(weights["l1/b"], OrderC))
    h, = Relu(None)(h)

    h, = Linear(None)(h, ConstantVariable(weights["l2/W"], OrderCN))
    h, = AxiswiseBias(None, axis=Axis.C)(h, ConstantVariable(weights["l2/b"], OrderC))
    h, = Relu(None)(h)

    h, = Linear(None)(h, ConstantVariable(weights["l3/W"], OrderCN))
    y, = AxiswiseBias(None, axis=Axis.C)(h, ConstantVariable(weights["l3/b"], OrderC))

    return Graph([x], [y])


def construct_graph_conv(weights: Dict[str, np.array], batch_size: int = 1) -> Graph:
    x = Variable([batch_size, 28, 28, 1], order=OrderNHWC)

    conv1 = Convolution2D(None, ksize=5, stride=1, padding=0)
    h, = conv1(x, ConstantVariable(weights["conv1/W"], OrderHWNC))
    h, = AxiswiseBias(None, axis=Axis.C)(h, ConstantVariable(weights["conv1/b"], OrderC))
    h, = Relu(None)(h)

    conv2 = Convolution2D(None, ksize=3, stride=2, padding=1)
    h, = conv2(h, ConstantVariable(weights["conv2/W"], OrderHWNC))
    h, = AxiswiseBias(None, axis=Axis.C)(h, ConstantVariable(weights["conv2/b"], OrderC))
    h, = Relu(None)(h)

    conv3 = Convolution2D(None, ksize=12, stride=1, padding=0)
    h, = conv3(h, ConstantVariable(weights["conv3/W"], OrderHWNC))
    y, = AxiswiseBias(None, axis=Axis.C)(h, ConstantVariable(weights["conv3/b"], OrderC))

    return Graph([x], [y])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("nn_type", choices=["fc", "conv"])
    parser.add_argument("--backend", default="webgpu", choices=["webgpu", "webassembly", "fallback"])
    parser.add_argument("--optimize", action="store_true")
    parser.add_argument("--encoding")
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

    graph_exec_data = generate_descriptor(args.backend, graph, constant_encoder_name=args.encoding)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    graph_exec_data.save(OUTPUT_DIR)


if __name__ == "__main__":
    main()
