import argparse
import os
from enum import Enum
from os import path

import chainer
import chainer.computational_graph
import numpy as np
# noinspection PyUnresolvedReferences
from model import FastStyleNet

from graph_builder.backend.interface.generator import generate_descriptor
from graph_builder.frontend.general_optimize_rule import GeneralOptimizeRule
from graph_builder.graph.converters.chainer import ChainerGraphConverter
from graph_builder.graph.graph import Graph
from graph_builder.graph.operator import Operator
from graph_builder.util.json import json

OUTPUT_DIR = path.join(path.dirname(__file__), "./output")


class NSTModelPath(Enum):
    starrynight = "../../resources/chainer-fast-neuralstyle-models/models/starrynight.model"
    scream = "../../resources/chainer-fast-neuralstyle-models/models/scream-style.model"
    fur = "../../resources/chainer-fast-neuralstyle-models/models/fur_0.model"
    candy = "../../resources/chainer-fast-neuralstyle-models/models/candy_512_2_49000.model"
    kanagawa = "../../resources/chainer-fast-neuralstyle-models/models/kanagawa.model"


def generate_graph(model_path: str) -> Graph:
    model = FastStyleNet()
    chainer.serializers.load_npz(model_path, model)

    # noinspection PyTypeChecker
    nn_input = chainer.Variable(np.zeros((1, 3, 384, 512), dtype=np.float32))

    # noinspection PyCallingNonCallable
    nn_output = model(nn_input, test=True)

    chainer_cg = chainer.computational_graph.build_computational_graph([nn_output])
    converter = ChainerGraphConverter()

    graph: Graph = converter.convert(chainer_cg, [nn_input], [nn_output])

    return graph


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=NSTModelPath.candy.name, choices=[v.name for v in NSTModelPath])
    parser.add_argument("--backend", default="webgpu", choices=["webgpu", "webassembly", "fallback"])
    parser.add_argument("--optimize", action="store_true")
    parser.add_argument("--encoding")
    args = parser.parse_args()

    model_path = NSTModelPath[args.model].value
    if not path.exists(model_path):
        raise FileNotFoundError(f"""Model data ({model_path}) is not found. Please clone 'https://github.com/gafr/chainer-fast-neuralstyle-models' under 
        the resource directory. Clone command takes about a few minute, and the repository size is about 200MB.""")

    graph = generate_graph(model_path)

    if args.optimize:
        graph, _ = GeneralOptimizeRule().optimize(graph)

    graph_exec_data = generate_descriptor(args.backend, graph, constant_encoder_name=args.encoding)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    graph_exec_data.save(OUTPUT_DIR)

if __name__ == "__main__":
    main()
