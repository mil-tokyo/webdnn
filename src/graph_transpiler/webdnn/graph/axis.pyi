from typing import Generic, Iterable, Tuple, TypeVar, overload, List


class Axis:
    def __init__(self, name: str = None): ...

    @property
    def id(self) -> int: pass

    @property
    def name(self) -> str: pass

    def unify(self, other: Axis): ...

    def __eq__(self, other) -> bool: ...

    def __str__(self) -> str: ...

    def __repr__(self) -> str: ...

    __hash__ = None

    N: Axis
    C: Axis
    H: Axis
    W: Axis
    T: Axis
    KH: Axis
    KW: Axis


T = TypeVar('T')


class AxisKeyDict(Generic[T]):
    @overload
    def __init__(self, other: AxisKeyDict): ...

    @overload
    def __init__(self, keys: Iterable[Axis], values: Iterable[T]): ...

    @overload
    def __init__(self, pairs: Iterable[Tuple[Axis, T]]): ...

    @overload
    def __init__(self): ...

    _keys: List[Axis]
    _values: List[T]

    def __contains__(self, item: Axis) -> bool: ...

    def __getitem__(self, item: Axis) -> T: ...

    def __setitem__(self, key: Axis, value: T): ...

    def __delitem__(self, key: Axis): ...

    def __len__(self) -> int: ...

    def __iter__(self) -> Iterable[Axis]: ...

    def __str__(self) -> str: ...

    def __repr__(self) -> str: ...

    def get(self, k: Axis, default: T) -> T: ...

    def keys(self) -> Iterable[Axis]: ...

    def values(self) -> Iterable[T]: ...

    def items(self) -> Iterable[Tuple[Axis, T]]: ...
