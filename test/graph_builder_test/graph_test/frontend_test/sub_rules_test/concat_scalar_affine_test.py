from nose import with_setup

from graph_builder.frontend.sub_rules.concat_scalar_affine import ConcatScalarAffine
from graph_builder.graph.graph import Graph
from graph_builder.graph.operators.scalar_affine import ScalarAffine
from graph_builder.graph.variable import Variable
from graph_builder.graph.variables.attributes.order import OrderNC
from graph_builder.optimize_rule.util import listup_operators
from graph_builder.util import flags
from test.util import FlagManager


class ConcatScalarAffineFlagManager(FlagManager):
    def get(self) -> bool:
        return flags.optimize.CONCAT_SCALAR_AFFINE

    def set(self, value: bool):
        flags.optimize.CONCAT_SCALAR_AFFINE = value


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
        graph, flag_changed = ConcatScalarAffine().optimize(graph)

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
        graph, flag_changed = ConcatScalarAffine().optimize(graph)

    ops = listup_operators(graph)
    assert len(ops) == 1 and isinstance(ops[0], ScalarAffine)
    assert ops[0].parameters["scale"] == 2 * 4 * 6
    assert ops[0].parameters["bias"] == (3 * 4 + 5) * 6 + 7
