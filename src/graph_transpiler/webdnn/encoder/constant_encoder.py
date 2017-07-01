from webdnn.backend.code_generator.allocator import MemoryLayout


class ConstantEncoder:
    name: str

    def encode(self, memory_layout: MemoryLayout) -> bytes:
        raise NotImplementedError()

    @classmethod
    def get_encoder(cls, name: str = None) -> "ConstantEncoder":
        # FIXME
        from webdnn.encoder.constant_encoder_raw import ConstantEncoderRaw
        from webdnn.encoder.constant_encoder_eightbit import ConstantEncoderEightbit
        if name is None or name == "raw":
            return ConstantEncoderRaw()
        elif name == "eightbit":
            return ConstantEncoderEightbit()
        else:
            raise ValueError("Unknown encoder")
