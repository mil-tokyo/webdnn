import warnings
from typing import Dict, Union, Tuple, List

import numpy as np

from webdnn.backend.code_generator.injector import Tag, Injector
from webdnn.graph.place_holder import PlaceHolder
from webdnn.util import flags

MetaBufferContent = Union[int, float, bytes, PlaceHolder]


class MetaInjector(Injector):
    def __init__(self):
        self.data = {}  # type: Dict[str, MetaBufferContent]
        self.offset_map = None  # type: Dict[str, int]
        self.buffer = None  # type: bytes
        self.arg_name = "meta_buffer"
        self.unresolved_value_list = []  # type: List[Tuple[int, PlaceHolder]]

    def register(self, data: Dict[str, MetaBufferContent]):
        self.data.update(data)

    def inject_tag(self, tag: Tag):
        """
        Inject MetaBuffer Tag

        %%META_NAME%%: get buffer name

            generated = injector.inject('std::string buffer_name = "%%META_NAME%%";')
            # >> generated == 'std::string buffer_name = "meta_buffer";'

        %%META_LOAD(key)%%: load buffer value

            injector.register({
                "test": 1234
            })

            generated = injector.inject("int test = %%META_LOAD(test)%%;")

            # >> generated == "int test = meta_buffer[0];"
            # buffer value is packed like "float[1] injector.buffer = {1234};"

        """
        if self.offset_map is None:
            self._generate_buffer()

        if tag.name == "META_NAME":
            return self.arg_name

        elif tag.name == "META_LOAD":
            key = tag.args[0]
            if key not in self.data:
                raise KeyError(f"key '{key}' is not registered in MetaBufferInjector.")

            if flags.optimize.OPTIMIZE and flags.optimize.EMBED_METABUFFER_VALUE:
                if isinstance(self.data[key], int) or isinstance(self.data[key], float):
                    return str(self.data[key])

                else:
                    return f"{self.arg_name}[{self.offset_map[key]}]"

            else:
                return f"{self.arg_name}[{self.offset_map[key]}]"

        else:
            return tag.original

    def _generate_buffer(self) -> bytes:
        if self.buffer:
            return self.buffer

        offset_map = {}
        buffer = bytes()
        for key, value in self.data.items():
            offset_map[key] = len(buffer) // 4  # sizeof(int)

            if isinstance(value, int) or isinstance(value, np.int32) or isinstance(value, np.int64):
                if isinstance(value, np.int64):
                    warnings.warn("np.int64 value is given to MetaBufferInjector and converted into int32 value.")

                buffer += np.array([value], dtype=np.int32).tobytes()

            elif isinstance(value, float) or isinstance(value, np.float32) or isinstance(value, np.float64):
                if isinstance(value, np.float64):
                    warnings.warn("np.float64 value is given to MetaBufferInjector and converted into float32 value.")

                buffer += np.array([value], dtype=np.float32).tobytes()

            elif isinstance(value, bytes):
                if len(value) % 4 != 0:
                    value += bytes(4 - (len(value) % 4))

                buffer += value

            elif isinstance(value, PlaceHolder):
                if PlaceHolder.check_resolved(value):
                    buffer += np.array([PlaceHolder.force_int(value)], dtype=np.int32).tobytes()

                else:
                    self.unresolved_value_list.append((len(buffer) // 4, value))
                    buffer += bytes(4)  # sizeof(int)

            else:
                raise TypeError("MetaBufferInjector supports only int, float, bytes, and resolved placeholder. "
                                + f"'{key}' is {type(value)}.")

        self.offset_map = offset_map
        self.buffer = buffer

        return self.buffer
