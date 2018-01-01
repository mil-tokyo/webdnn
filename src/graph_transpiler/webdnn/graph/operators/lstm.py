from typing import Optional

from webdnn.graph.axis import Axis
from webdnn.graph.operator import Operator
from webdnn.graph.order import OrderNTC, OrderNC, OrderC
from webdnn.graph.variable import Variable


class LSTM(Operator):
    """Long-short term memory layer.

    Currently, outputs value of hidden layer after final input is consumed.
    Details are corresponding to Keras's implementation (layers/recurrent.py)

    Args:
        name (str): Operator name.

    """

    def __init__(self, name: Optional[str], use_bias: bool, return_sequences: bool,
                 use_initial_c: bool, use_initial_h: bool,
                 activation: str, recurrent_activation: str):
        # TODO: accept selection of activation function
        super().__init__(name)
        self.parameters["use_bias"] = use_bias
        self.parameters["return_sequences"] = return_sequences
        self.parameters["use_initial_c"] = use_initial_c
        self.parameters["use_initial_h"] = use_initial_h
        assert activation in ["tanh"], "unknown activation function"
        self.parameters["activation"] = activation
        assert recurrent_activation in ["hard_sigmoid", "sigmoid"], "unknown recurrent activation function"
        self.parameters["recurrent_activation"] = recurrent_activation

    def __call__(self, x: Variable, w_input: Variable, w_hidden: Variable, b: Optional[Variable] = None,
                 initial_c: Optional[Variable] = None, initial_h: Optional[Variable] = None):
        """
        Args:
            x (:class:`~webdnn.graph.variable.Variable`): Input (sequence OrderNTC)
            w_input (:class:`~webdnn.graph.variable.Variable`): Weight for input
            w_hidden (:class:`~webdnn.graph.variable.Variable`): Weight for hidden state
            b (:class:`~webdnn.graph.variable.Variable`): Bias
            initial_c (:class:`~webdnn.graph.variable.Variable`): Initial cell state
            initial_h (:class:`~webdnn.graph.variable.Variable`): Initial hidden state

        Returns:
            y (:class:`~webdnn.graph.variable.Variable`): Output (OrderNC)
            final_c (:class:`~webdnn.graph.variable.Variable`): Last cell state (OrderNC)
        """
        assert self.parameters["use_bias"] == (b is not None)
        assert self.parameters["use_initial_c"] == (initial_c is not None)
        assert self.parameters["use_initial_h"] == (initial_h is not None)

        x_shape_dict = x.shape_dict
        w_input_shape_dict = w_input.shape_dict
        w_hidden_shape_dict = w_hidden.shape_dict

        assert x.order.check_same_axes(OrderNTC)
        assert w_input.order.check_same_axes(OrderNC)
        assert w_hidden.order.check_same_axes(OrderNC)
        assert b.order == OrderC

        batch_size = x_shape_dict[Axis.N]
        sequence_len = x_shape_dict[Axis.T]
        input_dim = x_shape_dict[Axis.C]
        hidden_dim = w_hidden_shape_dict[Axis.C]

        assert x_shape_dict[Axis.N] == batch_size
        assert x_shape_dict[Axis.C] == w_input_shape_dict[Axis.C] == input_dim
        assert w_input_shape_dict[Axis.N] == w_hidden_shape_dict[Axis.N] == hidden_dim * 4

        if initial_c is not None:
            initial_c_shape_dict = initial_c.shape_dict

            assert initial_c.order.check_same_axes(OrderNC)
            assert initial_c_shape_dict[Axis.N] == batch_size
            assert initial_c_shape_dict[Axis.C] == hidden_dim

        if initial_h is not None:
            initial_h_shape_dict = initial_h.shape_dict

            assert initial_h.order.check_same_axes(OrderNC)
            assert initial_h_shape_dict[Axis.N] == batch_size
            assert initial_h_shape_dict[Axis.C] == hidden_dim

        if self.parameters["return_sequences"]:
            y = Variable([batch_size, sequence_len, hidden_dim], OrderNTC)
            y.change_order(x.order)  # output same order as input to preserve following reshape semantics
        else:
            y = Variable([batch_size, hidden_dim], OrderNC)

        final_c = Variable([batch_size, hidden_dim], OrderNC)

        self.append_input("x", x)
        self.append_input("w_input", w_input)
        self.append_input("w_hidden", w_hidden)

        if b is not None:
            self.append_input("b", b)

        if initial_c is not None:
            self.append_input("initial_c", initial_c)

        if initial_h is not None:
            self.append_input("initial_h", initial_h)

        self.append_output("y", y)
        self.append_output("final_c", final_c)
        return y, final_c
