import numpy as np

from webdnn.graph.order import Order
from webdnn.graph.place_holder import PlaceHolder
from webdnn.graph.variable import Variable
from webdnn.graph.variables.attributes.constant import Constant


# FIXME: DOCS
class ConstantVariable(Variable):
    data: np.array

    def __init__(self, data: np.array, order: Order):
        super(ConstantVariable, self).__init__(data.shape, order)
        self.data = data
        self.attributes = {Constant(self)}

    def __repr__(self):
        order_repr = ''.join(map(lambda e: e.name, self.order.axes))
        return f"<Constant shape={self.shape}, order=\"{order_repr}\">"

    def change_order(self, order: Order):
        # 次元数を減らす時は、なくなる次元のサイズが1のときだけOK
        # 増える次元は、サイズ1
        current_shape_dict = self.shape_dict
        new_shape = [current_shape_dict.get(axis, PlaceHolder(1)) for axis in order.axes]
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
