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


def main():
    sys.setrecursionlimit(10000)  # workaround for deep copying large graph

    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="resnet50", choices=["vgg16", "resnet50"])
    parser.add_argument("--backend", default="webgpu,webassembly,fallback")
    parser.add_argument("--encoding")
    parser.add_argument('--out', '-o', default='output_chainer',
                        help='Directory to output the graph descriptor')

    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)

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

    any_backend_failed = False
    last_backend_exception = None
    for backend in args.backend.split(","):
        try:
            graph_exec_data = generate_descriptor(backend, graph, constant_encoder_name=args.encoding)
            graph_exec_data.save(args.out)
        except Exception as ex:
            any_backend_failed = True
            last_backend_exception = ex
            sys.stderr.write(f"Failed generating descriptor for backend {backend}: {str(ex)}\n")

    if any_backend_failed:
        raise last_backend_exception

if __name__ == "__main__":
    main()
