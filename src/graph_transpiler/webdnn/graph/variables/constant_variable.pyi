import numpy as np

from webdnn.graph.order import Order
from webdnn.graph.variable import Variable


class ConstantVariable(Variable):
    data: np.ndarray

    def __init__(self, data: np.ndarray, order: Order): ...

    def change_order(self, order: Order) -> ConstantVariable: ...
