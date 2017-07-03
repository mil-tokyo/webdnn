import keras

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
