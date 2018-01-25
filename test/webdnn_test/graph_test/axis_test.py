from nose.tools import raises

from webdnn.graph.axis import Axis, AxisKeyDict


def test_equal():
    a1 = Axis()
    assert a1 == a1


def test_equal_other_type():
    assert Axis() != 1


def test_not_equal():
    a1 = Axis()
    a2 = Axis()
    assert a1 != a2


def test_unify():
    a1 = Axis()
    a2 = Axis()
    a1.unify(a2)
    assert a1 == a2


def test_unify_same_axis():
    a1 = Axis()
    a1.unify(a1)
    assert a1 == a1


def test_unify_resolved_axes():
    a1 = Axis()
    a2 = Axis()
    a1.unify(a2)
    a1.unify(a2)
    assert a1 == a2


def test_unify_chain():
    a1 = Axis()
    a2 = Axis()
    a3 = Axis()
    a1.unify(a2)
    a1.unify(a3)
    assert a2 == a3


def test_unify_deep_chain():
    a1 = Axis()
    a2 = Axis()
    a3 = Axis()
    a4 = Axis()
    a1.unify(a2)
    a3.unify(a4)
    a1.unify(a3)
    assert a2 == a4


def test_unify_same_name_axes():
    a1 = Axis(name="A")
    a2 = Axis(name="A")
    a1.unify(a2)
    assert a1 == a2


@raises(TypeError)
def test_unify_different_name_axes():
    a1 = Axis(name="A")
    a2 = Axis(name="B")
    a1.unify(a2)


@raises(TypeError)
def test_unify_deep_chain_different_name_axes():
    a1 = Axis(name="A")
    a2 = Axis()
    a3 = Axis(name="B")
    a4 = Axis()
    a1.unify(a2)
    a3.unify(a4)
    a2.unify(a4)


def test_axis_key_dict_init_with_nothing():
    d1 = AxisKeyDict()
    assert len(d1) == 0


def test_axis_key_dict_init_with_other_dict():
    d1 = AxisKeyDict([Axis.N, Axis.C], [1, 3])
    d2 = AxisKeyDict(d1)
    assert d1 != d2
    assert d2[Axis.N] == 1
    assert d2[Axis.C] == 3


def test_axis_key_dict_init_with_pairs():
    d1 = AxisKeyDict([
        (Axis.N, 1),
        (Axis.C, 3)
    ])
    assert d1[Axis.N] == 1
    assert d1[Axis.C] == 3


def test_axis_key_dict_init_with_key_and_values():
    d1 = AxisKeyDict(
        [Axis.N, Axis.C],
        [1, 3]
    )
    assert d1[Axis.N] == 1
    assert d1[Axis.C] == 3


@raises(ValueError)
def test_axis_key_dict_init_with_duplicated_keys():
    AxisKeyDict(
        [Axis.N, Axis.N],
        [1, 3]
    )


@raises(ValueError)
def test_axis_key_dict_init_with_unpaired_sequences():
    AxisKeyDict(
        [Axis.N, Axis.C],
        [1, 3, 5]
    )


@raises(ValueError)
def test_axis_key_dict_init_with_invalid_arguments():
    # noinspection PyTypeChecker
    AxisKeyDict({1: Axis.N, 3: Axis.C})


def test_axis_key_dict_delitem():
    d1 = AxisKeyDict([
        (Axis.N, 1),
        (Axis.C, 3)
    ])
    assert Axis.N in d1
    del d1[Axis.N]
    assert Axis.N not in d1
    assert d1[Axis.C] == 3
