try:
    import keras
except ImportError as e:
    pass

from webdnn.frontend.keras.converter import KerasConverter
from webdnn.graph.operators.lstm import LSTM
from webdnn.graph.order import OrderC, OrderCN


# noinspection PyUnusedLocal
@KerasConverter.register_handler("SimpleRNN")
def _convert_simple_rnn(converter: KerasConverter, k_op: "keras.layers.SimpleRNN"):
    # TODO
    raise NotImplementedError('[KerasConverter] keras.layers.SimpleRNN is not supported')


# noinspection PyUnusedLocal
@KerasConverter.register_handler("GRU")
def _convert_gru(converter: KerasConverter, k_op: "keras.layers.GRU"):
    # TODO
    raise NotImplementedError('[KerasConverter] keras.layers.GRU is not supported')


@KerasConverter.register_handler("LSTM")
def _convert_lstm(converter: KerasConverter, k_op: "keras.layers.LSTM"):
    assert k_op.stateful is False, "[KerasConverter] Currently, LSTM.stateful is not supported"
    assert k_op.go_backwards is False, "[KerasConverter] Currently, LSTM.go_backwards is not supported"

    x = converter.get_variable(converter.get_input_tensor(k_op)[0])
    w_input = converter.convert_to_constant_variable(k_op.kernel, OrderCN)
    w_hidden = converter.convert_to_constant_variable(k_op.recurrent_kernel, OrderCN)

    if k_op.use_bias:
        b = converter.convert_to_constant_variable(k_op.bias, OrderC)

    else:
        b = None

    y, c = LSTM(None, k_op.use_bias, k_op.return_sequences,
                use_initial_c=False, use_initial_h=False,
                activation=k_op.activation.__name__,
                recurrent_activation=k_op.recurrent_activation.__name__)(x, w_input, w_hidden, b)

    k_outputs = converter.get_output_tensor(k_op)

    converter.set_variable(k_outputs[0], y)

    if k_op.return_state:
        converter.set_variable(k_outputs[1], None)
        converter.set_variable(k_outputs[2], c)
