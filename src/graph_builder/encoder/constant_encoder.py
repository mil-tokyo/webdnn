import numpy as np
from graph_builder.backend.interface.memory_layout import IMemoryLayout


class ConstantEncoder:
    name: str

    def encode(self, constant_layout: IMemoryLayout, data: np.ndarray) -> bytes:
        raise NotImplementedError()

    @classmethod
    def get_encoder(cls, name: str = None) -> "ConstantEncoder":
        from graph_builder.encoder.constant_encoder_raw import ConstantEncoderRaw
        from graph_builder.encoder.constant_encoder_eightbit import ConstantEncoderEightbit
        if name is None or name == "raw":
            return ConstantEncoderRaw()
        elif name == "eightbit":
            return ConstantEncoderEightbit()
        else:
            raise ValueError("Unknown encoder")
