import warnings

from nose.tools import raises

from webdnn.util.assertion import assert_sequence_type


def test_assert_sequence_type_auto_fix_with_list():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        v = assert_sequence_type([1.0, 2, 3.0], int, auto_fix=True, warning=True)

        assert len(w) == 1, len(w)
        assert isinstance(v, list), type(v)
        assert len(v) == 3, len(v)
        assert v[0] == 1, v[0]
        assert v[1] == 2, v[1]
        assert v[2] == 3, v[2]


def test_assert_sequence_type_auto_fix_with_tuple():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        v = assert_sequence_type((1.0, 2, 3.0), int, auto_fix=True, warning=False)

        assert len(w) == 0, len(w)
        assert isinstance(v, tuple), type(v)
        assert len(v) == 3, len(v)
        assert v[0] == 1, v[0]
        assert v[1] == 2, v[1]
        assert v[2] == 3, v[2]


@raises(TypeError)
def test_assert_sequence_type_raise_error():
    assert_sequence_type((1.0, 2, 3.0), int, auto_fix=False)
