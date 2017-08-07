import logging

logging.getLogger("tensorflow").setLevel(logging.WARNING)

# noinspection PyUnresolvedReferences
import tensorflow as tf

# noinspection PyUnresolvedReferences
from webdnn.frontend.tensorflow.converter import TensorFlowConverter
