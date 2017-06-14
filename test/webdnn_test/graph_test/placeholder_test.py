from webdnn.graph.place_holder import PlaceHolder


def test_resolved1():
    assert PlaceHolder(value=1) == 1


def test_resolved2():
    p = PlaceHolder()
    p.value = 1
    assert PlaceHolder(value=1) == p


def test_add1():
    p = PlaceHolder()
    q = p + 1
    p.value = 2
    assert q == 3


def test_add2():
    p = PlaceHolder()
    q = p + 1
    r = q + 2
    p.value = 2
    assert r == 5


def test_add3():
    p = PlaceHolder()
    q = p + 1
    r = 2 + q
    p.value = 2
    assert r == 5


def test_radd1():
    p = PlaceHolder()
    q = 1 + p
    p.value = 2
    assert q == 3


def test_radd2():
    p = PlaceHolder()
    q = 1 + p
    r = 2 + q
    p.value = 2
    assert r == 5


def test_radd3():
    p = PlaceHolder()
    q = 1 + p
    r = q + 2
    p.value = 2
    assert r == 5


def test_sub1():
    p = PlaceHolder()
    q = p - 2
    p.value = 3
    assert q == 1


def test_sub2():
    p = PlaceHolder()
    q = p - 2
    r = q - 1
    p.value = 3
    assert r == 0


def test_sub3():
    p = PlaceHolder()
    q = p - 2
    r = 2 - q
    p.value = 3
    assert r == 1


def test_rsub1():
    p = PlaceHolder()
    q = 1 - p
    p.value = 3
    assert q == -2


def test_rsub2():
    p = PlaceHolder()
    q = 1 - p
    r = 2 - q
    p.value = 2
    assert r == 3


def test_rsub3():
    p = PlaceHolder()
    q = 1 - p
    r = q - 2
    p.value = 2
    assert r == -3


def test_add_sub():
    p = PlaceHolder()
    q = p + 2
    r = q - 1
    p.value = 3
    assert r == 4


def test_mul1():
    p = PlaceHolder()
    q = p * 2
    p.value = 3
    assert q == 6


def test_mul2():
    p = PlaceHolder()
    q = p * 2
    r = q * 3
    p.value = 3
    assert r == 18


def test_mul3():
    p = PlaceHolder()
    q = p * 2
    r = 3 * q
    p.value = 3
    assert r == 18


def test_rmul1():
    p = PlaceHolder()
    q = 2 * p
    p.value = 3
    assert q == 6


def test_rmul2():
    p = PlaceHolder()
    q = 2 * p
    r = 3 * q
    p.value = 2
    assert r == 12


def test_rmul3():
    p = PlaceHolder()
    q = 2 * p
    r = q * 3
    p.value = 2
    assert r == 12


def test_floordiv():
    p = PlaceHolder()
    q = p // 3
    p.value = 7
    assert q == 2


def test_mod():
    p = PlaceHolder()
    q = p % 3
    p.value = 7
    assert q == 1
