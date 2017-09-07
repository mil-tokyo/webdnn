import numpy as np

from webdnn.graph.axis import AxisKeyDict
from webdnn.graph.order import Order
from webdnn.graph.variable import Variable
from webdnn.graph.variables.attributes.constant import Constant


class ConstantVariable(Variable):
    """ConstantVariable(data, order)

    Variable with constant data.

    Args:
        data (np.array): constant data.
        order (:class:`~webdnn.Order`): the data order.
    """

    def __init__(self, data: np.array, order: Order):
        super(ConstantVariable, self).__init__(data.shape, order)
        self.data = data.astype(np.float32)  # type: np.array
        self.attributes.add(Constant(self))

    def copy(self) -> "ConstantVariable":
        return ConstantVariable(self.data.copy(), self.order)

    def change_order(self, order: Order) -> "ConstantVariable":
        """change_order(order)

        Change variable order.

        When number of dimension will be increased, axes whose size is one are created.
        Conversely when number of dimension will be decreased, the size of axes which will be removed must be one.

        Not only order attribute, the data attribute is also modified.

        Args:
            order: new order
        """
        old_order = self.order
        old_shape_dict = AxisKeyDict(self.shape_dict.keys(), self.shape_dict.values())

        super().change_order(order)

        new_order = self.order
        new_shape_dict = AxisKeyDict(self.shape_dict.keys(), self.shape_dict.values())

        #
        # `old_order_common` and `new_order_common` represent axis orders about axes included in both `old_order` and `new_order`
        #
        # ex) old_order = OrderCHWN
        #     new_order = OrderNTC
        #
        # =>  old_order_common = OrderCN
        #     new_order_common = OrderNC
        #
        # Data is transposed as follow sequence:
        #
        #     +-----------+                +------------------+                  +------------------+                +-----------+
        #     | old_order |                | old_order_common |                  | new_order_common |                | new_order |
        #     |-----------|  -[reshape]->  |------------------|  -[transpose]->  |------------------|  -[reshape]->  |-----------|
        #     | OrderCHWN |                | OrderCN          |                  | OrderNC          |                | OrderNTC  |
        #     +-----------+                +------------------+                  +------------------+                +-----------+
        #

        old_order_common = Order([axis for axis in old_order.axes if axis in new_order.axes])
        new_order_common = Order([axis for axis in new_order.axes if axis in old_order.axes])

        data = self.data.reshape([old_shape_dict[axis] for axis in old_order_common.axes])
        data = np.transpose(data, tuple(old_order_common.axes_dict[axis] for axis in new_order_common.axes))
        data = data.reshape([new_shape_dict[axis] for axis in new_order.axes])

        self.data = data

        return self


def _broadcasted_order(order1: Order, order2: Order):
    axes = list(order1.axes)
    axes.extend([a for a in order2.axes if a not in order1.axes])
    return Order(axes)
