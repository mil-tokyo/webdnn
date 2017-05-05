from abc import abstractmethod
from typing import Type

import numpy as np

from graph_builder.graph.operator import Operator
from graph_builder.graph.variable import Variable
from graph_builder.graph.variables.attributes.order import OrderC, OrderNC, OrderCN, OrderNHWC, OrderHWNC, OrderHWCN, OrderCNHW, \
    OrderCHWN, OrderNCHW


def template_elementwise_operator(OperatorClass: Type[Operator]):
    orders = [OrderC, OrderNC, OrderCN, OrderNHWC, OrderHWNC, OrderHWCN, OrderNCHW, OrderCNHW, OrderCHWN]

    for order in orders:
        op = OperatorClass("op")

        x = Variable(np.arange(order.ndim) + 1, order)
        y, = op(x)
        for axis in y.axis_order.axes:
            assert y.shape_dict[axis] == x.shape_dict[axis]


class FlagManager:
    _tmp_value = None

    def __init__(self, target_value: bool = True):
        self.target_value = target_value

    def setup(self):
        self._tmp_value = self.get()
        self.set(self.target_value)

    def teardown(self):
        self.set(self._tmp_value)

    @abstractmethod
    def get(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def set(self, value: bool):
        raise NotImplementedError
