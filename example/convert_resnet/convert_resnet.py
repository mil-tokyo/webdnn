from os import path

import numpy as np
import chainer
import chainer.computational_graph

from graph_builder.graph import operators as O
from graph_builder.graph.graph import Variable
from graph_builder.graph.operators import attributes as A
from graph_builder.graph.variables import Constant
from graph_builder.optimizer import Optimizer
from graph_builder.graph.converters.chainer import ChainerGraphConverter

class SampleChain(chainer.Chain):
    def __init__(self):
        super().__init__(
            conv1=chainer.links.Convolution2D(3, 8, ksize=3, stride=2, pad=1),
            fc2=chainer.links.Linear(None, 10)
        )

    def __call__(self, x):
        h = chainer.functions.relu(self.conv1(x))
        h = self.fc2(h)
        return h

def main_resnet():
    link = chainer.links.model.vision.resnet.ResNet50Layers()
    dummy_input = chainer.Variable(np.random.rand(1, 3, 224, 224).astype(np.float32))#dummy image
    dummy_output = link(dummy_input, layers=['fc6'])['fc6']  # 'prob' is also possible (uses softmax)
    chainer_cg = chainer.computational_graph.build_computational_graph([dummy_output])
    converter = ChainerGraphConverter()
    graph = converter.convert(chainer_cg, [dummy_input], [dummy_output])
    graph.dump()

def main():
    link = SampleChain()
    dummy_input = chainer.Variable(np.random.rand(1, 3, 32, 32).astype(np.float32))
    dummy_output = link(dummy_input)
    chainer_cg = chainer.computational_graph.build_computational_graph([dummy_output])
    converter = ChainerGraphConverter()
    graph = converter.convert(chainer_cg, [dummy_input], [dummy_output])
    graph.dump()

if __name__ == "__main__":
    main()
