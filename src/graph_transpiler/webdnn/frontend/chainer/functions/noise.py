import chainer

from webdnn.frontend.chainer.converter import ChainerConverter
from webdnn.util import console


@ChainerConverter.register_handler("Dropout")
def _convert_dropout(converter: ChainerConverter, c_op: "chainer.functions.Dropout"):
    console.warning("[ChainerConverter] Dropout is ignored")

    x = converter.get_variable(c_op.inputs[0])

    converter.set_variable(c_op.outputs[0](), x)


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("Gaussian")
def _convert_gaussian(converter: ChainerConverter, c_op: "chainer.functions.Gaussian"):
    # TODO
    raise NotImplementedError("[ChainerConverter] Gaussian is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("SimplifiedDropconnect")
def _convert_simplified_dropconnect(converter: ChainerConverter, c_op: "chainer.functions.SimplifiedDropconnect"):
    # TODO
    raise NotImplementedError("[ChainerConverter] SimplifiedDropconnect is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("Zoneout")
def _convert_zoneout(converter: ChainerConverter, c_op: "chainer.functions.Zoneout"):
    # TODO
    raise NotImplementedError("[ChainerConverter] Zoneout is not supported")
