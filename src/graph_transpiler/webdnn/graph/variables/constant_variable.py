import numpy as np

from webdnn.graph.order import Order
from webdnn.graph.variable import Variable
from webdnn.graph.variables.attributes.constant import Constant


# FIXME: DOCS
class ConstantVariable(Variable):
    """
    Constant variable

    attrs:
        data (np.array) : data of the variable
    """
    data: np.array

    def __init__(self, data: np.array, order: Order):
        super(ConstantVariable, self).__init__(data.shape, order)
        self.data = data
        self.attributes = {Constant(self)}

    def change_order(self, order: Order) -> "ConstantVariable":
        """Change variable order

        When number of dimension will be increased, axes whose size is one are created.
        Conversely when number of dimension will be decreased, the size of axes which will be removed must be one.

        Args:
            order: new order
        """
        old_order = self.order

        super().change_order(order)

        new_order = self.order

        if set(old_order.axes) == set(new_order.axes):
            trans_axes = tuple(old_order.axes_dict[axis] for axis in new_order.axes)
            self.data = np.transpose(self.data, trans_axes)

        else:
            raise NotImplementedError("[ConstantVariable.change_order] Currently, it's not supported to increase or decrease axis")  # FIXME

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
        return ConstantVariable(self.data + other, self.order)

    def __radd__(self, other):
        return ConstantVariable(other + self.data, self.order)

    def __sub__(self, other):
        return ConstantVariable(self.data - other, self.order)

    def __rsub__(self, other):
        return ConstantVariable(other - self.data, self.order)

    def __mul__(self, other):
        return ConstantVariable(self.data * other, self.order)

    def __rmul__(self, other):
        return ConstantVariable(other * self.data, self.order)

    def __truediv__(self, other):
        return ConstantVariable(self.data / other, self.order)

    def __rtruediv__(self, other):
        return ConstantVariable(other / self.data, self.order)

    def __pow__(self, power, modulo=None):
        if modulo is not None:
            raise NotImplementedError("Variable.__pow__ is not supported modulo argument")

        else:
            return ConstantVariable(self.data ** power, self.order)

    def __rpow__(self, other):
        return ConstantVariable(other ** self.data, self.order)
