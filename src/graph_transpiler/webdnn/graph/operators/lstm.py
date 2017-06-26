from typing import Optional

from webdnn.graph.axis import Axis
from webdnn.graph.order import OrderNTC, OrderNT, OrderNC, OrderCN, OrderC
from webdnn.graph.operator import Operator
from webdnn.graph.variable import Variable


class LSTM(Operator):
    """Long-short term memory layer.

    Currently, outputs value of hidden layer after final input is consumed.
    Details are corresponding to Keras's implementation (layers/recurrent.py)

    Args:
        name (str): Operator name.

    """

    def __init__(self, name: Optional[str], use_bias: bool, return_sequences: bool, use_initial_c: bool):
        # TODO: accept selection of activation function
        super().__init__(name)
        self.parameters["use_bias"] = use_bias
        self.parameters["return_sequences"] = return_sequences
        self.parameters["use_initial_c"] = use_initial_c
        self.attributes = set()

    def __call__(self, x: Variable, w_input: Variable, w_hidden: Variable, b: Optional[Variable]=None, initial_c: Optional[Variable]=None):
        """
        Args:
            x (:class:`~webdnn.graph.variable.Variable`): Input (sequence OrderNTC)
            w_input (:class:`~webdnn.graph.variable.Variable`): Weight for input
            w_hidden (:class:`~webdnn.graph.variable.Variable`): Weight for hidden state
            b (:class:`~webdnn.graph.variable.Variable`): Bias
            initial_c (:class:`~webdnn.graph.variable.Variable`): Initial hidden state

        Returns:
            tuple of :class:`~webdnn.graph.variable.Variable`: Output (OrderNC)
        """
        self.append_input("x", x)
        self.append_input("w_input", w_input)
        self.append_input("w_hidden", w_hidden)
        assert self.parameters["use_bias"] == (b is not None)
        if self.parameters["use_bias"]:
            self.append_input("b", b)
        assert self.parameters["use_initial_c"] == (initial_c is not None)
        if initial_c is not None:
            self.append_input("initial_c", initial_c)

        x_shape_dict = x.shape_dict
        w_input_shape_dict = w_input.shape_dict
        w_hidden_shape_dict = w_hidden.shape_dict
        batch_size = x_shape_dict[Axis.N]
        assert x.order == OrderNTC
        assert w_input.order == OrderNC or w_input.order == OrderCN
        assert b.order == OrderC
        assert x_shape_dict[Axis.C] == w_input_shape_dict[Axis.C]
        sequence_len = x_shape_dict[Axis.T]
        hidden_dim = w_input_shape_dict[Axis.N] // 4
        assert hidden_dim * 4 == w_hidden_shape_dict[Axis.N] and hidden_dim == w_hidden_shape_dict[Axis.C]
        assert hidden_dim * 4 == b.shape_dict[Axis.C]
        if self.parameters["return_sequences"]:
            y = Variable([batch_size, sequence_len, hidden_dim], OrderNTC)
        else:
            y = Variable([batch_size, hidden_dim], OrderNC)
        final_c = Variable([batch_size, hidden_dim], OrderNC)
        self.append_output("y", y)
        self.append_output("final_c", final_c)
        return y, final_c
