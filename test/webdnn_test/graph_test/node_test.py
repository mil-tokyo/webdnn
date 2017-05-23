from webdnn.graph.node import Node


def test_append_prev():
    n1 = Node()
    n2 = Node()
    n2.append_prev(n1)

    assert n1.prevs == set()
    assert n1.nexts == {n2}
    assert n2.prevs == {n1}
    assert n2.nexts == set()


def test_remove_prev():
    n1 = Node()
    n2 = Node()
    n2.append_prev(n1)
    n2.remove_prev(n1)

    assert n1.prevs == set()
    assert n1.nexts == set()
    assert n2.prevs == set()
    assert n2.nexts == set()


def test_append_next():
    n1 = Node()
    n2 = Node()
    n1.append_next(n2)

    assert n1.prevs == set()
    assert n1.nexts == {n2}
    assert n2.prevs == {n1}
    assert n2.nexts == set()


def test_remove_next():
    n1 = Node()
    n2 = Node()
    n1.append_next(n2)
    n1.remove_next(n2)

    assert n1.prevs == set()
    assert n1.nexts == set()
    assert n2.prevs == set()
    assert n2.nexts == set()
