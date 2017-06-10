from abc import ABCMeta
from typing import List, Type, Dict, Set, Tuple, Optional, Union

from webdnn.graph.axis import Axis
from webdnn.graph.order import Order
from webdnn.graph.place_holder import PlaceHolder


class IAttribute:
    node: "INode"


class INode:
    attributes: Set[IAttribute]
    parameters: Dict[str, any]
    prevs: Set["INode"]
    nexts: Set["INode"]

    # noinspection PyUnusedLocal
    def __init__(self, name: Optional[str]):
        raise NotImplementedError

    def append_prev(self, prev: "INode"):
        raise NotImplementedError

    def remove_prev(self, prev: "INode"):
        raise NotImplementedError

    def append_next(self, next: "INode"):
        raise NotImplementedError

    def remove_next(self, next: "INode"):
        raise NotImplementedError

    def __repr__(self):
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError


class IVariable(INode, metaclass=ABCMeta):
    shape: List[Union[int, PlaceHolder]]
    input_to: Set["IOperator"]
    output_from: "IOperator"
    order: Order

    # noinspection PyUnusedLocal,PyMissingConstructor
    def __init__(self, shape: List[Union[int, PlaceHolder]], order: Order):
        raise NotImplementedError

    @property
    def name(self) -> str:
        raise NotImplementedError

    @name.setter
    def name(self, name: str) -> None:
        raise NotImplementedError

    @property
    def size(self) -> Union[int, PlaceHolder]:
        raise NotImplementedError

    @property
    def ndim(self) -> int:
        raise NotImplementedError

    @property
    def shape_dict(self) -> Dict[Axis, Union[int, PlaceHolder]]:
        raise NotImplementedError

    def change_order(self, order: Order) -> None:
        raise NotImplementedError

    def __repr__(self) -> str:
        raise NotImplementedError

    def __str__(self) -> str:
        raise NotImplementedError


class IOperator(INode, metaclass=ABCMeta):
    inputs: Dict[str, IVariable]
    outputs: Dict[str, IVariable]

    def get_input_name(self, var: IVariable) -> None:
        raise NotImplementedError

    def get_output_name(self, var: IVariable) -> str:
        raise NotImplementedError

    def append_input(self, name: str, var: IVariable) -> None:
        raise NotImplementedError

    def remove_input(self, var: IVariable) -> None:
        raise NotImplementedError

    def replace_input(self, v_old: IVariable, v_new: IVariable) -> None:
        raise NotImplementedError

    def append_output(self, name: str, var: IVariable) -> None:
        raise NotImplementedError

    def remove_output(self, var: IVariable) -> None:
        raise NotImplementedError

    def replace_output(self, v_old: IVariable, v_new: IVariable) -> None:
        raise NotImplementedError

    def remove_all(self) -> None:
        raise NotImplementedError

    def __repr__(self) -> str:
        raise NotImplementedError

    def __str__(self) -> str:
        raise NotImplementedError

    def __call__(self, *args, **kwargs) -> Tuple[IVariable]:
        raise NotImplementedError

    def get_attribute(self, Attr: Type[IAttribute]) -> List[IAttribute]:
        raise NotImplementedError
