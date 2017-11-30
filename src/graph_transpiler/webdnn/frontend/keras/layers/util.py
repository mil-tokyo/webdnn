from webdnn.graph.order import OrderNCHW, OrderNHWC

try:
    import keras
except ImportError as e:
    pass

from webdnn.graph.operators.elu import Elu
from webdnn.graph.operators.hard_sigmoid import HardSigmoid
from webdnn.graph.operators.relu import Relu
from webdnn.graph.operators.sigmoid import Sigmoid
from webdnn.graph.operators.softmax import Softmax
from webdnn.graph.operators.softplus import Softplus
from webdnn.graph.operators.softsign import Softsign
from webdnn.graph.operators.tanh import Tanh
from webdnn.graph.variable import Variable


def do_activation(activation: any, x: Variable) -> Variable:
    if activation is keras.activations.relu:
        return Relu(None)(x)[0]

    elif activation is keras.activations.sigmoid:
        return Sigmoid(None)(x)[0]

    elif activation is keras.activations.hard_sigmoid:
        return HardSigmoid(None)(x)[0]

    elif activation is keras.activations.softplus:
        return Softplus(None, beta=1.0)(x)[0]

    elif activation is keras.activations.softsign:
        return Softsign(None)(x)[0]

    elif activation is keras.activations.softmax:
        return Softmax(None, axis=x.order.axes[-1])(x)[0]

    elif activation is keras.activations.elu:
        return Elu(None)(x)[0]

    elif activation is keras.activations.tanh:
        return Tanh(None)(x)[0]

    elif activation is keras.activations.linear:
        return x

    else:
        raise NotImplementedError(f"[KerasConverter] Unknown activation: {activation}")


def check_data_format(v: Variable, data_format: str):
    if data_format == "channels_first":
        v.order.unify(OrderNCHW)

    elif data_format == "channels_last":
        v.order.unify(OrderNHWC)

    else:
        raise ValueError(f"[KerasConverter] Unknown data format: {data_format}")


def parse_padding(padding_type: str, ksize: int, dilation_rate: int) -> int:
    if padding_type == "valid":
        return 0

    elif padding_type == "same":
        # @see https://github.com/tensorflow/tensorflow/blob/e5cf6f0c13b6053e4c58af6a951b204fde263172/tensorflow/python/ops/nn_ops.py#L507-L519
        dilated_ksize = ksize + (ksize - 1) * (dilation_rate - 1)
        pad_extra_shape = dilated_ksize - 1

        if pad_extra_shape % 2 != 0:
            raise NotImplementedError(f"""
[KerasConverter] Currently WebDNN doesn't supports different size padding: 
    (pad_extra_shape)=f{pad_extra_shape}""")

        return pad_extra_shape // 2

    else:
        raise ValueError(f"[KerasConverter] Unknown padding: {padding_type}")
