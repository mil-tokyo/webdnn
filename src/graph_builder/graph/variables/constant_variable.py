from typing import Type

import numpy as np

from graph_builder.graph.variable import Variable
from graph_builder.graph.variables.attributes.constant import Constant
from graph_builder.graph.variables.attributes.order import AxisOrder


# FIXME: DOCS
class ConstantVariable(Variable):
    data: np.array

    def __init__(self, data: np.array, order: Type[AxisOrder]):
        super(ConstantVariable, self).__init__(data.shape, order)
        self.data = data
        self.attributes.add(Constant)

    def __repr__(self):
        order_repr = ''.join(map(lambda e: e.name, self.order.axes))
        return f"<Constant shape={self.shape}, order=\"{order_repr}\">"

    def change_order(self, order: Type[AxisOrder]):
        # 次元数を減らす時は、なくなる次元のサイズが1のときだけOK
        # 増える次元は、サイズ1
        current_shape_dict = self.shape_dict
        new_shape = [current_shape_dict.get(axis, 1) for axis in order.axes]
        for axis, size in current_shape_dict.items():
            if axis not in order.axes:
                assert size == 1

        if len(self.order.axes) == len(order.axes):
            #  新しい軸がもとの軸で何番目かを列挙
            trans_axes = tuple(self.order.axes_dict[axis] for axis in order.axes)
            self.data = np.transpose(self.data, trans_axes)
        else:
            #  別に実装できないわけではないが手抜き
            raise NotImplementedError()

        self.order = order
        self.shape = new_shape
