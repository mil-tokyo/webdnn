import logging

logging.getLogger("tensorflow").setLevel(logging.WARNING)

# noinspection PyUnresolvedReferences
import keras
import keras.backend as K

K.set_learning_phase(0)

# noinspection PyUnresolvedReferences
import tensorflow

# noinspection PyUnresolvedReferences
from webdnn.frontend.keras.converter import KerasConverter
