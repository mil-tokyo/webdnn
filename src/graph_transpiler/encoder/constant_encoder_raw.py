import numpy as np

from graph_transpiler.backend.interface.memory_layout import IMemoryLayout
from graph_transpiler.encoder.constant_encoder import ConstantEncoder


class ConstantEncoderRaw(ConstantEncoder):
    def __init__(self):
        self.name = "raw"

    def encode(self, constant_layout: IMemoryLayout, data: np.ndarray) -> bytes:
        return data.tobytes("C")
