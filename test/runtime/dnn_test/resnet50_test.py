import chainer
import numpy as np

from test.util import generate_kernel_test_case
from webdnn.frontend.chainer.converter import ChainerConverter


def test():
    vx = chainer.Variable(np.zeros((1, 3, 224, 224), dtype=np.float32))
    link = chainer.links.model.vision.resnet.ResNet50Layers()
    if chainer.__version__ >= "2.":
        with chainer.using_config('train', False):
            nn_outputs = link(vx, layers=['fc6'])
    else:
        nn_outputs = link(vx, layers=['fc6'], test=False)
    vy = nn_outputs["fc6"]

    graph = ChainerConverter().convert([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[dnn] chainer.links.model.vision.resnet.ResNet50Layers",
        graph=graph,
        backend=["webgpu", "webgl", "webassembly"],
        inputs={x: vx.data},
        expected={y: vy.data},
        EPS=1e-2,
    )
