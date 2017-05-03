from typing import Dict, Union

import numpy as np

from graph_builder.backend.webassembly.tag_parser import TagParser
from graph_builder.util import flags

MetaBufferContent = Union[int, float, bytes]


class MetaBufferInjector:
    def __init__(self):
        self.data = {}  # type: Dict[str, MetaBufferContent]
        self.offset_map = None  # type: Dict[str, int]
        self.buffer = None  # type: bytes
        self.arg_name = "meta_buffer"

    def register(self, data: Dict[str, any]):
        self.data.update(data)

    def inject(self, source: str) -> str:
        if self.offset_map is None:
            self.generate_buffer()

        for tag in TagParser.parse(source):
            if tag.name == "META_NAME":  # メタバッファ名の取得
                source = source[:tag.span[0]] + self.arg_name + source[tag.span[1]:]

            elif tag.name == "META_LOAD":  # データの読み込み
                key = tag.args[0]
                if key not in self.data:
                    raise KeyError(f"key '{key}' is not registered in MetaBufferInjector.")

                if flags.optimize.EMBED_METABUFFER_VALUE:
                    value = self.data[key]
                    if isinstance(value, int) or isinstance(value, float):
                        value = str(value)

                    else:
                        value = f"{self.arg_name}[{self.offset_map[key]}]"

                else:
                    value = f"{self.arg_name}[{self.offset_map[key]}]"

                source = source[:tag.span[0]] + value + source[tag.span[1]:]

        return source

    def generate_buffer(self) -> bytes:
        if self.buffer:
            return self.buffer

        offset_map = {}
        buffer = bytes()
        for key, value in self.data.items():
            offset_map[key] = len(buffer) // 4  # sizeof(int)

            if isinstance(value, int):
                buffer += np.array([value], dtype=np.int32).tobytes()

            elif isinstance(value, float):
                buffer += np.array([value], dtype=np.float32).tobytes()

            elif isinstance(value, bytes):
                if len(value) % 4 != 0:
                    value += bytes(4 - (len(value) % 4))
                    
                buffer += value

            else:
                raise TypeError("MetaBufferInjector supports only int, float, and bytes contents.")

        self.offset_map = offset_map
        self.buffer = buffer

        return self.buffer
