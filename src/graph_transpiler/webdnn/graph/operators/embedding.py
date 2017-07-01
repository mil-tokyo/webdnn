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
        self.attributes = set()

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

        # @TODO: this is too strict condition. It should be supported in optimization phase, not here.
        if x.order != OrderNT:
            raise NotImplementedError("Currently, Embedding supports only OrderNT variable for input sequence variable.")

        x_shape_dict = x.shape_dict
        w_shape_dict = w.shape_dict

        assert set(w.order.axes) == {Axis.N, Axis.C}

        batch_size = x_shape_dict[Axis.N]
        sequence_len = x_shape_dict[Axis.T]
        embedding_dim = w_shape_dict[Axis.N]

        y = Variable([batch_size, sequence_len, embedding_dim], OrderNTC)

        self.append_output("y", y)
        return y,
