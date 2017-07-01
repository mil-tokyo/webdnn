from nose import with_setup

from test.util import FlagManager
from webdnn.graph.axis import Axis
from webdnn.optimizer.sub_rules.remove_last_softmax import RemoveLastSoftmax
from webdnn.graph.graph import Graph
from webdnn.graph.operators.linear import Linear
from webdnn.graph.operators.softmax import Softmax
from webdnn.graph.order import OrderCN, OrderNC
from webdnn.graph.traverse import listup_operators
from webdnn.graph.variable import Variable
from webdnn.util import flags

orders2 = [OrderNC, OrderCN]

tmp_flag = None


class RemoveLastSoftmaxFlagManager(FlagManager):
    def get(self) -> bool:
        return flags.optimize.REMOVE_LAST_SOFTMAX

    def set(self, value: bool):
        flags.optimize.REMOVE_LAST_SOFTMAX = value


flag_manager = RemoveLastSoftmaxFlagManager()


@with_setup(flag_manager.setup, flag_manager.teardown)
def test_single_softmax():
    linear = Linear('linear')
    softmax = Softmax('softmax', axis=Axis.C)

    x = Variable([4, 5], OrderNC)
    w = Variable([4, 5], OrderNC)
    h, = linear(x, w)
    y, = softmax(h)

    graph = Graph([x], [y])

    graph, _ = RemoveLastSoftmax().optimize(graph)

    ops = listup_operators(graph)
    assert len(ops) == 1 and isinstance(ops[0], Linear)
    assert len(graph.outputs) == 1 and ops[0].outputs["y"] == graph.outputs[0]


@with_setup(flag_manager.setup, flag_manager.teardown)
def test_double_softmax():
    linear = Linear('linear')
    softmax1 = Softmax('softmax', axis=Axis.C)
    softmax2 = Softmax('softmax', axis=Axis.C)

    x = Variable([4, 5], OrderNC)
    w = Variable([4, 5], OrderNC)
    h, = linear(x, w)
    h, = softmax1(h)
    y, = softmax2(h)

    graph = Graph([x], [y])

    graph, _ = RemoveLastSoftmax().optimize(graph)

    ops = listup_operators(graph)
    assert len(ops) == 1 and isinstance(ops[0], Linear)
    assert len(graph.outputs) == 1 and ops[0].outputs["y"] == graph.outputs[0]


@with_setup(flag_manager.setup, flag_manager.teardown)
def test_internal_softmax():
    linear1 = Linear('linear')
    softmax1 = Softmax('softmax', axis=Axis.C)
    linear2 = Linear('linear')
    softmax2 = Softmax('softmax', axis=Axis.C)

    x = Variable([4, 5], OrderNC)
    w1 = Variable([4, 5], OrderNC)
    w2 = Variable([3, 4], OrderNC)
    h, = linear1(x, w1)
    h, = softmax1(h)
    h, = linear2(h, w2)
    y, = softmax2(h)

    graph = Graph([x], [y])

    graph, _ = RemoveLastSoftmax().optimize(graph)

    ops = listup_operators(graph)
    assert len(ops) == 3 and isinstance(ops[0], Linear) and isinstance(ops[1], Softmax) and isinstance(ops[2], Linear)
    assert len(graph.outputs) == 1 and ops[2].outputs["y"] == graph.outputs[0]
