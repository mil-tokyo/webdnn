from abc import ABCMeta
from typing import List, Type, Dict, Set, Tuple

from graph_transpiler.graph.variables.attributes.order import AxisOrder


class IVariable(metaclass=ABCMeta):
    shape: List[int]
    input_to: Set["IOperator"]
    output_from: "IOperator"
    order: Type[AxisOrder]

    # noinspection PyUnusedLocal
    def __init__(self, shape: List[int], order: Type[AxisOrder]):
        raise NotImplementedError

    @property
    def name(self) -> str:
        raise NotImplementedError

    @name.setter
    def name(self, name: str) -> None:
        raise NotImplementedError

    @property
    def size(self) -> int:
        raise NotImplementedError

    @property
    def ndim(self) -> int:
        raise NotImplementedError

    @property
    def shape_dict(self):
        raise NotImplementedError

    def change_order(self, order: Type[AxisOrder]) -> None:
        raise NotImplementedError

    def __repr__(self) -> str:
        raise NotImplementedError

    def __str__(self) -> str:
        raise NotImplementedError


class IOperator(metaclass=ABCMeta):
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
