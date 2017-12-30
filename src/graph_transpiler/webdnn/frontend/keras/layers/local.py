import keras

from webdnn.frontend.keras.converter import KerasConverter


# noinspection PyUnusedLocal
@KerasConverter.register_handler("LocallyConnected1D")
def _convert_locally_connected1d(converter: KerasConverter, k_op: "keras.layers.LocallyConnected1D"):
    # TODO
    raise NotImplementedError('[KerasConverter] keras.layers.LocallyConnected1D is not supported')


# noinspection PyUnusedLocal
@KerasConverter.register_handler("LocallyConnected2D")
def _convert_locally_connected2d(converter: KerasConverter, k_op: "keras.layers.LocallyConnected2D"):
    # TODO
    raise NotImplementedError('[KerasConverter] keras.layers.LocallyConnected2D is not supported')
