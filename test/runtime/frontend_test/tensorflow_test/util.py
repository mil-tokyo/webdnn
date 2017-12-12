import logging

logging.getLogger("tensorflow").setLevel(logging.WARNING)

# noinspection PyUnresolvedReferences
import tensorflow as tf  # noqa

# noinspection PyUnresolvedReferences
from webdnn.frontend.tensorflow.converter import TensorFlowConverter  # noqa
