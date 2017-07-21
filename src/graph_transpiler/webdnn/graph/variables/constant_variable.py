import numpy as np

from webdnn.graph.order import Order
from webdnn.graph.variable import Variable
from webdnn.graph.variables.attributes.constant import Constant


# FIXME: DOCS
class ConstantVariable(Variable):
    """ConstantVariable(data, order)

    Variable with constant data.

    Args:
        data (np.array): constant data.
        order (:class:`~webdnn.Order`): the data order.
    """
    data: np.array

    def __init__(self, data: np.array, order: Order):
        super(ConstantVariable, self).__init__(data.shape, order)
        self.data = data
        self.attributes = {Constant(self)}

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
        old_shape_dict = dict(self.shape_dict)

        super().change_order(order)

        new_order = self.order
        new_shape_dict = dict(self.shape_dict)

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

    # Unary operators
    def __pos__(self):
        return ConstantVariable(self.data.copy(), self.order)

    def __neg__(self):
        return ConstantVariable(-self.data.copy(), self.order)

    def __abs__(self):
        return ConstantVariable(np.abs(self.data), self.order)

    # Binary operators
    def __add__(self, other):
        if isinstance(other, ConstantVariable):
            v2 = ConstantVariable(other.data.copy(), other.order)
            v2.change_order(self.order)

            return ConstantVariable(self.data + v2.data, self.order)

        else:
            return super(ConstantVariable, self).__add__(other)

    def __radd__(self, other):
        if isinstance(other, ConstantVariable):
            v2 = ConstantVariable(other.data.copy(), other.order)
            v2.change_order(self.order)

            return ConstantVariable(v2.data + self.data, self.order)

        else:
            return super(ConstantVariable, self).__radd__(other)

    def __sub__(self, other):
        if isinstance(other, ConstantVariable):
            v2 = ConstantVariable(other.data.copy(), other.order)
            v2.change_order(self.order)

            return ConstantVariable(self.data - v2.data, self.order)

        else:
            return super(ConstantVariable, self).__sub__(other)

    def __rsub__(self, other):
        if isinstance(other, ConstantVariable):
            v2 = ConstantVariable(other.data.copy(), other.order)
            v2.change_order(self.order)

            return ConstantVariable(v2.data - self.data, self.order)

        else:
            return super(ConstantVariable, self).__rsub__(other)

    def __mul__(self, other):
        if isinstance(other, ConstantVariable):
            v2 = ConstantVariable(other.data.copy(), other.order)
            v2.change_order(self.order)

            return ConstantVariable(self.data * v2.data, self.order)

        else:
            return super(ConstantVariable, self).__mul__(other)

    def __rmul__(self, other):
        if isinstance(other, ConstantVariable):
            v2 = ConstantVariable(other.data.copy(), other.order)
            v2.change_order(self.order)

            return ConstantVariable(v2.data * self.data, self.order)

        else:
            return super(ConstantVariable, self).__rmul__(other)

    def __truediv__(self, other):
        if isinstance(other, ConstantVariable):
            v2 = ConstantVariable(other.data.copy(), other.order)
            v2.change_order(self.order)

            return ConstantVariable(self.data / v2.data, self.order)

        else:
            return super(ConstantVariable, self).__truediv__(other)

    def __rtruediv__(self, other):
        if isinstance(other, ConstantVariable):
            v2 = ConstantVariable(other.data.copy(), other.order)
            v2.change_order(self.order)

            return ConstantVariable(v2.data / self.data, self.order)

        else:
            return super(ConstantVariable, self).__rtruediv__(other)

    def __pow__(self, power, modulo=None):
        if modulo is not None:
            raise NotImplementedError("Variable.__pow__ is not supported modulo argument")

        elif isinstance(power, ConstantVariable):
            v2 = ConstantVariable(power.data.copy(), power.shape)
            v2.change_order(self.order)

            return ConstantVariable(self.data ** v2.data, self.order)

        else:
            return super(ConstantVariable, self).__pow__(power)

    def __rpow__(self, other):
        if isinstance(other, ConstantVariable):
            v2 = ConstantVariable(other.data.copy(), other.order)
            v2.change_order(self.order)

            return ConstantVariable(v2.data ** self.data, self.order)

        else:
            return super(ConstantVariable, self).__rpow__(other)
