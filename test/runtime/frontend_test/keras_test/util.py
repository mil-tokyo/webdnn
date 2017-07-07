import logging

logging.getLogger("tensorflow").setLevel(logging.WARNING)

# noinspection PyUnresolvedReferences
import keras

# noinspection PyUnresolvedReferences
from webdnn.frontend.keras.converter import KerasConverter
