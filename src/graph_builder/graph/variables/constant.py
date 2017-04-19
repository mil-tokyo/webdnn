import numpy as np

from graph_builder.graph.graph import Variable
from graph_builder.graph.operators import attributes as A


class Constant(Variable):
    attributes = {A.Constant}
    data: np.array

    def __init__(self, data: np.array):
        self.data = data

        super(Constant, self).__init__(data.shape)
