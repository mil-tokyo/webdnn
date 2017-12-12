import chainer

from webdnn.frontend.chainer.converter import ChainerConverter
from webdnn.util import console


@ChainerConverter.register_handler("Dropout")
def _convert_dropout(converter: ChainerConverter, c_op: "chainer.functions.Dropout"):
    console.warning("[ChainerConverter] Dropout is ignored")

    x = converter.get_variable(c_op.inputs[0])

    converter.set_variable(c_op.outputs[0](), x)

# TODO: Gaussian

# TODO: SimplifiedDropconnect

# TODO: Zoneout
