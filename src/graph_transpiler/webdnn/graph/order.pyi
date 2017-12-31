from typing import Tuple, Sequence, Union

from webdnn.graph.axis import Axis, AxisKeyDict


class Order:
    _axes: Tuple[Axis, ...]

    def __init__(self, axes: Sequence[Union[Axis, None]]): ...

    @property
    def axes(self) -> Tuple[Axis, ...]: ...

    @property
    def ndim(self) -> int: ...

    @property
    def axes_dict(self) -> AxisKeyDict[int]: ...

    def __eq__(self, other) -> bool: ...

    def __repr__(self) -> str: ...

    def __str__(self) -> str: ...

    def check_same_axes(self, other: Order) -> bool: ...

    def get_common_axes(self, other: Order) -> Sequence[Axis]: ...

    def get_all_axes(self, other: Order) -> Sequence[Axis]: ...

    def unify(self, other: Order): ...


OrderC: Order
OrderNC: Order
OrderCN: Order
OrderNHWC: Order
OrderHWNC: Order
OrderHWCN: Order
OrderNCHW: Order
OrderCNHW: Order
OrderCHWN: Order
OrderNT: Order
OrderNTC: Order
