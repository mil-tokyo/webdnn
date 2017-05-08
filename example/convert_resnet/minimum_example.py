import chainer
import numpy as np

from graph_builder.backend.interface.generator import generate_descriptor
from graph_builder.graph.converters.chainer import ChainerGraphConverter

#  Load chainer pretrained model
model = chainer.links.model.vision.resnet.ResNet50Layers()

#  Execute model with dummy data. In chainer, computation graph are defined by
#  run. Therefore we need execute model at least once to construct the graph.
x = chainer.Variable(np.empty((1, 3, 224, 224), dtype=np.float32))
y = model(x, layers=["fc6"])["fc6"]

#  Convert chainer computation graph to our computation graph format
graph = ChainerGraphConverter().convert_from_inout_vars([x], [y])

#  Generate and save execution information
exec_info = generate_descriptor("webgpu", graph)
exec_info.save("./output")
