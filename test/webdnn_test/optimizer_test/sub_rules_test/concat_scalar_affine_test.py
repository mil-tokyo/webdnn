from nose import with_setup

from test.util import FlagManager
from webdnn.graph.graph import Graph
from webdnn.graph.operators.scalar_affine import ScalarAffine
from webdnn.graph.order import OrderNC
from webdnn.graph.traverse import listup_operators
from webdnn.graph.variable import Variable
from webdnn.optimizer.sub_rules.concat_scalar_operation import ConcatScalarOperation
from webdnn.util import flags


class ConcatScalarAffineFlagManager(FlagManager):
    def get(self) -> bool:
        return flags.optimize.CONCAT_SCALAR_OPERATION

    def set(self, value: bool):
        flags.optimize.CONCAT_SCALAR_OPERATION = value


flag_manager = ConcatScalarAffineFlagManager()


@with_setup(flag_manager.setup, flag_manager.teardown)
def test_double_affine():
    affine1 = ScalarAffine(None, scale=2, bias=3)
    affine2 = ScalarAffine(None, scale=4, bias=5)

    x = Variable([5, 5], OrderNC)

    h, = affine1(x)
    y, = affine2(h)

    graph = Graph([x], [y])

    flag_changed = True
    while flag_changed:
        graph, flag_changed = ConcatScalarOperation().optimize(graph)

    ops = listup_operators(graph)
    assert len(ops) == 1 and isinstance(ops[0], ScalarAffine)
    assert ops[0].parameters["scale"] == 2 * 4
    assert ops[0].parameters["bias"] == 3 * 4 + 5


@with_setup(flag_manager.setup, flag_manager.teardown)
def test_triple_affine():
    affine1 = ScalarAffine(None, scale=2, bias=3)
    affine2 = ScalarAffine(None, scale=4, bias=5)
    affine3 = ScalarAffine(None, scale=6, bias=7)

    x = Variable([5, 5], OrderNC)

    h, = affine1(x)
    h, = affine2(h)
    y, = affine3(h)

    graph = Graph([x], [y])

    flag_changed = True
    while flag_changed:
        graph, flag_changed = ConcatScalarOperation().optimize(graph)

    ops = listup_operators(graph)
    assert len(ops) == 1 and isinstance(ops[0], ScalarAffine)
    assert ops[0].parameters["scale"] == 2 * 4 * 6
    assert ops[0].parameters["bias"] == (3 * 4 + 5) * 6 + 7
