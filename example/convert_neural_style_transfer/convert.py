import argparse
import sys
from enum import Enum
from os import path

import chainer
import numpy as np
from model import FastStyleNet

from webdnn.backend import generate_descriptor
from webdnn.frontend.chainer import ChainerConverter


class NSTModelPath(Enum):
    starrynight = "../../resources/chainer-fast-neuralstyle-models/models/starrynight.model"
    scream = "../../resources/chainer-fast-neuralstyle-models/models/scream-style.model"
    fur = "../../resources/chainer-fast-neuralstyle-models/models/fur_0.model"
    candy = "../../resources/chainer-fast-neuralstyle-models/models/candy_512_2_49000.model"
    kanagawa = "../../resources/chainer-fast-neuralstyle-models/models/kanagawa.model"


sys.setrecursionlimit(10000)
parser = argparse.ArgumentParser()
parser.add_argument("--model", default=NSTModelPath.kanagawa.name, choices=[v.name for v in NSTModelPath])
parser.add_argument("--backend", default="webgpu", choices=["webgpu", "webassembly", "fallback"])
parser.add_argument("--encoding")
args = parser.parse_args()

print(f"model: {args.model}")
print(f"backend: {args.backend}")
print(f"encoding: {args.encoding}")

# Load chainer pre-trained model
model = FastStyleNet()

model_path = NSTModelPath[args.model].value
if not path.exists(model_path):
    raise FileNotFoundError(f"Model data ({model_path}) is not found. Please clone " +
                            "'https://github.com/gafr/chainer-fast-neuralstyle-models' under the resource directory. " +
                            "Clone command takes about a few minute, the repository size is about 200MB.")

chainer.serializers.load_npz(model_path, model)

# Execute forward propagation to construct computation graph
if chainer.__version__ >= "2.":
    with chainer.using_config("train", False):  # fixes batch normalization
        x = chainer.Variable(np.zeros((1, 3, 144, 192), dtype=np.float32))
        y = model(x)
else:
    x = chainer.Variable(np.zeros((1, 3, 144, 192), dtype=np.float32))
    y = model(x, test=False)

# Convert chainer computation graph into IR
graph = ChainerConverter().convert([x], [y])

# Generate graph descriptor
generate_descriptor(args.backend, graph, constant_encoder_name=args.encoding).save(path.join(path.dirname(__file__), "./output"))
