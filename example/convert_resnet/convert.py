"""
Example of converting ResNet-50 Chainer model
"""

import argparse
import sys
import os
from os import path

import chainer
import chainer.computational_graph
import numpy as np

from webdnn.backend.interface.generator import generate_descriptor
from webdnn.graph.converters.chainer import ChainerGraphConverter

OUTPUT_DIR = path.join(path.dirname(__file__), "./output")


def main():
    sys.setrecursionlimit(10000)  # workaround for deep copying large graph

    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="vgg16", choices=["vgg16", "resnet50"])
    parser.add_argument("--backend", default="webgpu", choices=["webgpu", "webassembly", "fallback"])
    parser.add_argument("--encoding")
    args = parser.parse_args()

    sample_image = np.zeros((224, 224, 3), dtype=np.uint8)#PIL.Image.open("")
    if args.model == "vgg16":
        link = chainer.links.model.vision.vgg.VGG16Layers()
        prepared_image = chainer.links.model.vision.vgg.prepare(sample_image)  # BGR, CHW
        out_layer_name = "fc8"

    elif args.model == "resnet50":
        link = chainer.links.model.vision.resnet.ResNet50Layers()
        prepared_image = chainer.links.model.vision.resnet.prepare(sample_image)
        out_layer_name = "fc6"

    nn_input = chainer.Variable(np.array([prepared_image], dtype=np.float32))
    nn_output = link(nn_input, layers=[out_layer_name])[out_layer_name]  # 'prob' is also possible (uses softmax)
    chainer_cg = chainer.computational_graph.build_computational_graph([nn_output])
    converter = ChainerGraphConverter()
    graph = converter.convert(chainer_cg, [nn_input], [nn_output])  # type: Graph

    graph_exec_data = generate_descriptor(args.backend, graph, constant_encoder_name=args.encoding)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    graph_exec_data.save(OUTPUT_DIR)

if __name__ == "__main__":
    main()
