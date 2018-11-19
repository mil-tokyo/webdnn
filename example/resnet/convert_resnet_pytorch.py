"""
Example of converting ResNet-50 PyTorch model
"""

import argparse
import os

import torch, torchvision
import numpy as np

from webdnn.backend import generate_descriptor, backend_names
from webdnn.frontend.pytorch import PyTorchConverter
from webdnn.util import console


def generate_graph():
    model = torchvision.models.resnet50(pretrained=True)
    dummy_input = torch.autograd.Variable(torch.zeros(1, 3, 224, 224))
    graph = PyTorchConverter().convert(model, dummy_input)
    return graph


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", default=",".join(backend_names))
    parser.add_argument("--encoding")
    parser.add_argument('--out', '-o', default='output_pytorch',
                        help='Directory to output the graph descriptor')

    graph = generate_graph()

    args = parser.parse_args()
    os.makedirs(args.out, exist_ok=True)

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
