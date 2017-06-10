from typing import Iterable, Union, Dict

import numpy as np

from webdnn.graph.axis import Axis
from webdnn.graph.interface import IVariable
from webdnn.graph.node import Node
from webdnn.graph.order import Order
# FIXME: DOCS
from webdnn.graph.place_holder import PlaceHolder


class Variable(Node, IVariable):
    """
    レイヤー間で受け渡される変数
    名前で識別される
    現在のところ、float32型(4byte/element)を想定している
    shapeはlist[int]で、その順序はAttribute(OrderNC etc)に依存
    """

    def __init__(self, shape: Iterable[Union[int, PlaceHolder]], order: Order):
        super().__init__()

        self.shape = list(shape)
        self.input_to = set()
        self.output_from = None
        self.order = order

        assert self.order.ndim == len(self.shape)

    @property
    def name(self):
        return self.parameters["name"] if "name" in self.parameters else ""

    @name.setter
    def name(self, name: str):
        self.parameters["name"] = name

    @property
    def size(self) -> Union[int, PlaceHolder]:
        return np.product(self.shape)

    @property
    def ndim(self):
        return len(self.shape)

    @property
    def shape_dict(self) -> Dict[Axis, Union[int, PlaceHolder]]:
        return dict(zip(self.order.axes, self.shape))

    def change_order(self, order: Order):
        # 次元数を減らす時は、なくなる次元のサイズが1のときだけOK
        # 増える次元は、サイズ1
        current_shape_dict = self.shape_dict
        new_shape = [current_shape_dict.get(axis, 1) for axis in order.axes]
        for axis, size in current_shape_dict.items():
            if axis not in order.axes:
                assert size == 1
        self.order = order
        self.shape = new_shape

    def __repr__(self):
        order_repr = ''.join(map(lambda e: e.name, self.order.axes))
        return f"<Variable {self.name} shape={self.shape}, order=\"{order_repr}\">"

    def __str__(self):
        return self.__repr__()
