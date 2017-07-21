from webdnn.graph.graph import Graph
from webdnn.graph.operator import Operator
from webdnn.graph.operators.scalar_affine import ScalarAffine
from webdnn.graph.order import OrderNC
from webdnn.graph.traverse import listup_operators
from webdnn.graph.variable import Variable
from webdnn.optimizer.sub_rules.remove_no_effect_operator import RemoveNoEffectOperator


def fn(x: Variable):
    y = Variable(x.shape, x.order)
    op = Operator(None)

    op.append_input("x", x)
    op.append_output("y", y)

    return y


def test_scalar_affine1():
    x = Variable([5, 5], OrderNC)
    h = fn(x)
    y, = ScalarAffine(None, scale=1, bias=0)(h)

    graph = Graph([x], [y])

    flag_changed = True
    while flag_changed:
        graph, flag_changed = RemoveNoEffectOperator().optimize(graph)

    ops = listup_operators(graph)
    assert len(ops) == 1 and type(ops[0]) is Operator


def test_scalar_affine2():
    x = Variable([5, 5], OrderNC)
    h = fn(x)
    y, = ScalarAffine(None, scale=2, bias=0)(h)

    graph = Graph([x], [y])

    flag_changed = True
    while flag_changed:
        graph, flag_changed = RemoveNoEffectOperator().optimize(graph)

    ops = listup_operators(graph)
    assert len(ops) == 2


def test_scalar_add1():
    x = Variable([5, 5], OrderNC)
    h = fn(x)
    y = h + 0

    graph = Graph([x], [y])

    flag_changed = True
    while flag_changed:
        graph, flag_changed = RemoveNoEffectOperator().optimize(graph)

    ops = listup_operators(graph)
    assert len(ops) == 1 and type(ops[0]) is Operator


def test_scalar_add2():
    x = Variable([5, 5], OrderNC)
    h = fn(x)
    y = h + 1

    graph = Graph([x], [y])

    flag_changed = True
    while flag_changed:
        graph, flag_changed = RemoveNoEffectOperator().optimize(graph)

    ops = listup_operators(graph)
    assert len(ops) == 2


def test_scalar_sub1():
    x = Variable([5, 5], OrderNC)
    h = fn(x)
    y = h - 0

    graph = Graph([x], [y])

    flag_changed = True
    while flag_changed:
        graph, flag_changed = RemoveNoEffectOperator().optimize(graph)

    ops = listup_operators(graph)
    assert len(ops) == 1 and type(ops[0]) is Operator


def test_scalar_sub2():
    x = Variable([5, 5], OrderNC)
    h = fn(x)
    y = h - 1

    graph = Graph([x], [y])

    flag_changed = True
    while flag_changed:
        graph, flag_changed = RemoveNoEffectOperator().optimize(graph)

    ops = listup_operators(graph)
    assert len(ops) == 2


def test_scalar_mul1():
    x = Variable([5, 5], OrderNC)
    h = fn(x)
    y = h * 1

    graph = Graph([x], [y])

    flag_changed = True
    while flag_changed:
        graph, flag_changed = RemoveNoEffectOperator().optimize(graph)

    ops = listup_operators(graph)
    assert len(ops) == 1 and type(ops[0]) is Operator


def test_scalar_mul2():
    x = Variable([5, 5], OrderNC)
    h = fn(x)
    y = h * 2

    graph = Graph([x], [y])

    flag_changed = True
    while flag_changed:
        graph, flag_changed = RemoveNoEffectOperator().optimize(graph)

    ops = listup_operators(graph)
    assert len(ops) == 2


def test_scalar_div1():
    x = Variable([5, 5], OrderNC)
    h = fn(x)
    y = h / 1

    graph = Graph([x], [y])

    flag_changed = True
    while flag_changed:
        graph, flag_changed = RemoveNoEffectOperator().optimize(graph)

    ops = listup_operators(graph)
    assert len(ops) == 1 and type(ops[0]) is Operator


def test_scalar_div2():
    x = Variable([5, 5], OrderNC)
    h = fn(x)
    y = h / 2

    graph = Graph([x], [y])

    flag_changed = True
    while flag_changed:
        graph, flag_changed = RemoveNoEffectOperator().optimize(graph)

    ops = listup_operators(graph)
    assert len(ops) == 2


def test_scalar_pow1():
    x = Variable([5, 5], OrderNC)
    h = fn(x)
    y = h ** 1

    graph = Graph([x], [y])

    flag_changed = True
    while flag_changed:
        graph, flag_changed = RemoveNoEffectOperator().optimize(graph)

    ops = listup_operators(graph)
    assert len(ops) == 1 and type(ops[0]) is Operator


def test_scalar_pow2():
    x = Variable([5, 5], OrderNC)
    h = fn(x)
    y = h ** 2

    graph = Graph([x], [y])

    flag_changed = True
    while flag_changed:
        graph, flag_changed = RemoveNoEffectOperator().optimize(graph)

    ops = listup_operators(graph)
    assert len(ops) == 2
