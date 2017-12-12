import logging

logging.getLogger("tensorflow").setLevel(logging.WARNING)

# noinspection PyUnresolvedReferences
import keras  # noqa
import keras.backend as K  # noqa

K.set_learning_phase(0)

# noinspection PyUnresolvedReferences
import tensorflow  # noqa

# noinspection PyUnresolvedReferences
from webdnn.frontend.keras.converter import KerasConverter  # noqa
