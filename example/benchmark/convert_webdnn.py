import sys

import chainer
import numpy as np

from webdnn.backend.interface.generator import generate_descriptor
from webdnn.graph.converters.chainer import ChainerGraphConverter
from webdnn.util import flags

sys.setrecursionlimit(10000)

model = chainer.links.model.vision.resnet.ResNet50Layers()

x = chainer.Variable(np.empty((1, 3, 224, 224), dtype=np.float32))
y = model(x, layers=["fc6"])["fc6"]

for backend in ('webgpu', 'webassembly'):
    for flag_optimize in (True, False):
        print(f"- Generating descriptor: backend=\033[0;32m{backend}\033[0;39m optimize=\033[0;32m{flag_optimize}\033[0;39m")

        flags.optimize.OPTIMIZE = flag_optimize
        output_dir = f"output/webdnn/resnet50/{'optimized' if flag_optimize else 'non_optimized'}"
        graph = ChainerGraphConverter().convert_from_inout_vars([x], [y])

        generate_descriptor(backend, graph).save(output_dir)
