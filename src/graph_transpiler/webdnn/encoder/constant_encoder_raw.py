from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.encoder.constant_encoder import ConstantEncoder


class ConstantEncoderRaw(ConstantEncoder):
    def __init__(self):
        self.name = "raw"

    def encode(self, memory_layout: MemoryLayout) -> bytes:
        return memory_layout.data.tobytes("C")
