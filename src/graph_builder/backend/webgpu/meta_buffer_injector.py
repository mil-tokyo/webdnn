from collections import OrderedDict
from typing import Dict
import numpy as np

from graph_builder.backend.webgpu.tag_parser import TagParser


class MetaBufferInjector:
    def __init__(self):
        self.data = {}  # type: Dict[str, any]
        self.offset_map = None  # type: Dict[str, int]
        self.buffer = None  # type: byte
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

                value = f"{self.arg_name}[{self.offset_map[key]}]"
                source = source[:tag.span[0]] + value + source[tag.span[1]:]

        return source

    def generate_buffer(self) -> bytes:
        if self.buffer:
            return self.buffer

        offset_map = {}
        offset = 0
        values = []
        for key, value in self.data.items():
            values += [value]
            offset_map[key] = offset
            offset += 1

        self.offset_map = offset_map
        self.buffer = np.array(values, dtype=np.int32).tobytes()

        return self.buffer
