import keras

from webdnn.frontend.keras.converter import KerasConverter


# noinspection PyUnusedLocal
@KerasConverter.register_handler("TimeDistributed")
def _convert_time_distributed(converter: KerasConverter, k_op: "keras.layers.TimeDistributed"):
    # TODO
    raise NotImplementedError('[KerasConverter] keras.layers.TimeDistributed is not supported')


# noinspection PyUnusedLocal
@KerasConverter.register_handler("Bidirectional")
def _convert_bidirectional(converter: KerasConverter, k_op: "keras.layers.Bidirectional"):
    # TODO
    raise NotImplementedError('[KerasConverter] keras.layers.Bidirectional is not supported')
