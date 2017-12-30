import keras

from webdnn.frontend.keras.converter import KerasConverter


# noinspection PyUnusedLocal
@KerasConverter.register_handler("GaussianNoise")
def _convert_gaussian_noise(converter: KerasConverter, k_op: "keras.layers.GaussianNoise"):
    # TODO
    raise NotImplementedError('[KerasConverter] keras.layers.GaussianNoise is not supported')


# noinspection PyUnusedLocal
@KerasConverter.register_handler("GaussianDropout")
def _convert_gaussian_dropout(converter: KerasConverter, k_op: "keras.layers.GaussianDropout"):
    # TODO
    raise NotImplementedError('[KerasConverter] keras.layers.GaussianDropout is not supported')
