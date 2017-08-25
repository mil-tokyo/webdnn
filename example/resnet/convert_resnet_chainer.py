"""
Example of converting ResNet-50 Chainer model
"""

import argparse
import os
import sys

import chainer
import chainer.computational_graph
import numpy as np

from webdnn.backend import generate_descriptor
from webdnn.frontend.chainer import ChainerConverter
from webdnn.util import console


def main():
    sys.setrecursionlimit(10000)  # workaround for deep copying large graph

    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="resnet50", choices=["vgg16", "resnet50"])
    parser.add_argument("--backend", default="webgpu,webgl,webassembly,fallback")
    parser.add_argument("--encoding")
    parser.add_argument('--out', '-o', default='output_chainer',
                        help='Directory to output the graph descriptor')

    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)

    sample_image = np.zeros((224, 224, 3), dtype=np.uint8)  # PIL.Image.open("")
    if args.model == "vgg16":
        link = chainer.links.model.vision.vgg.VGG16Layers()
        prepared_image = chainer.links.model.vision.vgg.prepare(sample_image)  # BGR, CHW

    elif args.model == "resnet50":
        link = chainer.links.model.vision.resnet.ResNet50Layers()
        prepared_image = chainer.links.model.vision.resnet.prepare(sample_image)

    else:
        raise NotImplementedError

    nn_input = chainer.Variable(np.array([prepared_image], dtype=np.float32))

    if chainer.__version__ >= "2.":
        with chainer.using_config('train', False):
            nn_output = link(nn_input, layers=['prob'])['prob']

    else:
        nn_output = link(nn_input, layers=['prob'], test=True)['prob']

    graph = ChainerConverter().convert([nn_input], [nn_output])  # type: Graph

    any_backend_failed = False
    last_backend_exception = None
    for backend in args.backend.split(","):
        try:
            graph_exec_data = generate_descriptor(backend, graph, constant_encoder_name=args.encoding)
            graph_exec_data.save(args.out)
        except Exception as ex:
            any_backend_failed = True
            last_backend_exception = ex
            console.error(f"Failed generating descriptor for backend {backend}: {str(ex)}\n")

    if any_backend_failed:
        raise last_backend_exception


if __name__ == "__main__":
    main()
