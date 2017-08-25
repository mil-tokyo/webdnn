"""
Example of converting ResNet-50 Keras model
"""

import argparse
import sys

from keras.applications import resnet50

from webdnn.backend import generate_descriptor
from webdnn.frontend.keras import KerasConverter
from webdnn.util import console


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="resnet50", choices=["resnet50"])
    parser.add_argument('--out', '-o', default='output_keras',
                        help='Directory to output the graph descriptor')
    parser.add_argument("--encoding", help="name of weight encoder")
    parser.add_argument("--backend", default="webgpu,webgl,webassembly,fallback", help="backend")
    args = parser.parse_args()

    model = resnet50.ResNet50(include_top=True, weights='imagenet')

    sys.setrecursionlimit(10000)
    graph = KerasConverter(batch_size=1).convert(model)
    for backend in args.backend.split(","):
        graph_exec_data = generate_descriptor(backend, graph, constant_encoder_name=args.encoding)
        graph_exec_data.save(args.out)

    console.stderr("Done.")


if __name__ == "__main__":
    main()
