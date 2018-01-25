import keras

from webdnn.frontend.keras.converter import KerasConverter
from webdnn.graph.operators.lstm import LSTM
from webdnn.graph.order import OrderC, OrderCN, OrderNTC


# noinspection PyUnusedLocal
@KerasConverter.register_handler("GRU")
def _convert_gru(converter: KerasConverter, k_op: "keras.layers.GRU"):
    # TODO
    raise NotImplementedError('[KerasConverter] keras.layers.GRU is not supported')


@KerasConverter.register_handler("LSTM")
def _convert_lstm(converter: KerasConverter, k_op: "keras.layers.LSTM"):
    assert k_op.stateful is False, "[KerasConverter] Currently, LSTM.stateful is not supported"
    assert k_op.go_backwards is False, "[KerasConverter] Currently, LSTM.go_backwards is not supported"

    # Structure of LSTM layer was changed in v2.0.9 (https://github.com/fchollet/keras/pull/7943)
    if "2.0.9" <= keras.__version__:
        cell = k_op.cell  # type: keras.layers.LSTMCell
    else:
        cell = k_op  # type: keras.layers.LSTM

    x = converter.get_variable(converter.get_input_tensor(k_op)[0])
    x.order.unify(OrderNTC)
    w_input = converter.convert_to_constant_variable(cell.kernel, OrderCN)
    w_hidden = converter.convert_to_constant_variable(cell.recurrent_kernel, OrderCN)

    if k_op.use_bias:
        b = converter.convert_to_constant_variable(cell.bias, OrderC)

    else:
        b = None

    y, c = LSTM(None, cell.use_bias, k_op.return_sequences,
                use_initial_c=False, use_initial_h=False,
                activation=cell.activation.__name__,
                recurrent_activation=cell.recurrent_activation.__name__)(x, w_input, w_hidden, b)

    k_outputs = converter.get_output_tensor(k_op)

    converter.set_variable(k_outputs[0], y)

    if k_op.return_state:
        # noinspection PyTypeChecker
        converter.set_variable(k_outputs[1], None)
        converter.set_variable(k_outputs[2], c)


# noinspection PyUnusedLocal
@KerasConverter.register_handler("SimpleRNN")
def _convert_simple_rnn(converter: KerasConverter, k_op: "keras.layers.SimpleRNN"):
    # TODO
    raise NotImplementedError('[KerasConverter] keras.layers.SimpleRNN is not supported')
