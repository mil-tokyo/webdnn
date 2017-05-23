import numpy as np

from webdnn.backend.interface.memory_layout import IMemoryLayout
from webdnn.encoder.constant_encoder import ConstantEncoder


class ConstantEncoderRaw(ConstantEncoder):
    def __init__(self):
        self.name = "raw"

    def encode(self, constant_layout: IMemoryLayout, data: np.ndarray) -> bytes:
        return data.tobytes("C")
