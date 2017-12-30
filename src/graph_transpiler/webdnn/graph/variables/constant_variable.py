import numpy as np

from webdnn.graph.axis import AxisKeyDict
from webdnn.graph.order import Order
from webdnn.graph.variable import Variable


class ConstantVariable(Variable):
    """ConstantVariable(data, order)

    Variable with constant data.

    Args:
        data (np.array): constant data.
        order (:class:`~webdnn.Order`): the data order.
    """

    def __init__(self, data: np.ndarray, order: Order):
        super(ConstantVariable, self).__init__(data.shape, order)
        self.data = data.copy().astype(np.float32)  # type: np.ndarray

    def change_order(self, order: Order) -> "ConstantVariable":
        """change_order(order)

        Change variable order.

        When number of dimension will be increased, axes whose size is one are created.
        Conversely when number of dimension will be decreased, the size of axes which will be removed must be one.

        Args:
            order: new order
        """
        old_order = self.order
        old_shape_dict = AxisKeyDict(self.shape_dict)

        super().change_order(order)

        new_order = self.order
        new_shape_dict = AxisKeyDict(self.shape_dict)

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
