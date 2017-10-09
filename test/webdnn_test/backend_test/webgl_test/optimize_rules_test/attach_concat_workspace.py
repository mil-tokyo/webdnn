from webdnn import Axis
from webdnn.backend.webgl.optimize_rules.attach_concat_workspace import AttachConcatWorkspace
from webdnn.frontend.chainer.converter import ChainerConverter
from webdnn.graph.operators.concat import Concat
from webdnn.graph.order import OrderNCHW
from webdnn.graph.variable import Variable


def test_attach():
    x = Variable((2, 3, 4, 5), OrderNCHW)
    y, = Concat(None, axis=Axis.N)(x)

    graph = ChainerConverter().convert([x], [y])

    assert len(graph.inputs) == 1
    AttachConcatWorkspace().optimize(graph)
    assert len(graph.inputs) == 2
    AttachConcatWorkspace().optimize(graph)
    assert len(graph.inputs) == 2
