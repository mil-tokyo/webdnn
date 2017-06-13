from typing import Optional

from webdnn.graph.axis import Axis
from webdnn.graph.order import OrderNTC, OrderNT, OrderNC, OrderCN
from webdnn.graph.operator import Operator
from webdnn.graph.variable import Variable


class Embedding(Operator):
    """Word embedding layer.

    Args:
        name (str): Operator name.

    """

    def __init__(self, name: Optional[str]):
        super().__init__(name)
        self.attributes = {}

    def __call__(self, x: Variable, w: Variable):
        """
        Args:
            x (:class:`~webdnn.graph.variable.Variable`): Input (sequence)
            w (:class:`~webdnn.graph.variable.Variable`): Weight

        Returns:
            tuple of :class:`~webdnn.graph.variable.Variable`: Output
        """
        self.append_input("x", x)
        self.append_input("w", w)

        x_shape_dict = x.shape_dict
        w_shape_dict = w.shape_dict
        batch_size = x_shape_dict[Axis.N]
        assert x.order == OrderNT
        assert w.order == OrderNC or w.order == OrderCN
        sequence_len = x_shape_dict[Axis.T]
        # n_vocabulary = w_shape_dict[Axis.C]
        embedding_dim = w_shape_dict[Axis.N]
        y = Variable([batch_size, sequence_len, embedding_dim], OrderNTC)
        self.append_output("y", y)
        return y,
