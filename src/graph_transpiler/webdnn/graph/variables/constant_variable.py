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

    def change_order(self, order: Order):
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
