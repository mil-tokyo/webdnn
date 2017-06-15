import warnings
from typing import Dict, Union, Tuple, List, Any

import numpy as np

from webdnn.backend.code_generator.allocator import Allocation, BufferType
from webdnn.backend.code_generator.injector import Tag, Injector
from webdnn.graph.place_holder import PlaceHolder

Content = Union[
    int,
    float,
    bytes,
    Allocation,
    PlaceHolder,
    List[Union[int, PlaceHolder]],
    List[Allocation]
]


def _flatten(l: List[Any]):
    """
    _flatten([[1, 2], 3, [[4], 5, [[6, 7]]], [8, 9]] == [1, 2, 3, 4, 5, 6, 7, 8, 9]
    """
    return sum([_flatten(v) if isinstance(v, list) else [v] for v in l], [])


class BufferInjector(Injector):
    def __init__(self,
                 meta_name: str = "meta_buffer",
                 static_name: str = "static_buffer",
                 dynamic_name: str = "dynamic_buffer"):

        self.value_map = {}  # type: Dict[str, Content]
        self.offset_map = None  # type: Dict[str, int]
        self.buffer = None  # type: bytes
        self.meta_name = meta_name
        self.static_name = static_name
        self.dynamic_name = dynamic_name
        self.unresolved_value_list = []  # type: List[Tuple[int, PlaceHolder]]

    def register(self, data: Dict[str, Content]):
        if self.offset_map is not None:
            raise ValueError("BufferInjector#register must be called before BufferInjector#inject is called.")

        self.value_map.update(data)

    def inject_tag(self, tag: Tag):
        """
        Inject BufferInjector Tag. Supported tags are as follows.

        `%%META_BUFFER%%` : get name of meta buffer:

            buffer_injector = BufferInjector()
            buffer_injector.inject('std::string meta_buffer_name = "%%META_BUFFER%%";')

            # >> 'std::string meta_buffer_name = "meta_buffer";'

        `%%STATIC_BUFFER%%` : get name of static buffer:

            buffer_injector = BufferInjector()
            buffer_injector.inject('std::string static_buffer_name = "%%STATIC_BUFFER%%";')

            # >> 'std::string static_buffer_name = "static_buffer";'

        `%%DYNAMIC_BUFFER%%` : get name of dynamic buffer:

            buffer_injector = BufferInjector()
            buffer_injector.inject('std::string dynamic_buffer_name = "%%DYNAMIC_NAME%%";')

            # >> 'std::string dynamic_buffer_name = "dynamic_buffer";'

        `%%LOAD_BUFFER(key)%%` : load buffer value:

            buffer_injector = BufferInjector()
            buffer_injector.register({
                "op_X": memory_layout[op_X],    # dynamic variable allocation
                "op_W": memory_layout[op_W],    # static variable allocation
                "op_N_B": 2                     # scalar value
                "op_Bs": [                      # list of variable allocations
                    memory_layout[op_B1],
                    memory_layout[op_B2]
                ]
            })

            buffer_injector.inject('''
                float       *X = %%LOAD_BUFFER(op_X)%%;
                const float *W = %%LOAD_BUFFER(op_W)%%;
                const int    N = %%LOAD_BUFFER(op_N_B)%%;

                for (int i = 0; i < N_B; i++)
                {
                    const float B_i = %%LOAD_BUFFER(op_Bs, i)%%
                }
            ''')

            # >> '''
            #    float       *X = (dynamic_buffer + meta_buffer[0]);  // For both cases, variable address is correctly resolved
            #    const float *W = (static_buffer + meta_buffer[1]);   // based on offset value (meta_buffer[0] and meta_buffer[1])
            #    const int    N = meta_buffer[2]
            #
            #    for (int i = 0; i < N_B; i++)
            #    {
            #        const float B_i = (meta_buffer[3+2+(i)] ? static_buffer : dynamic_buffer)[ meta_buffer[3 + (i)] ]
            #    }
            # '''
            #
            # int meta_buffer[7] = {
            #   op_X.offset, op_W.offset, 2
            #   op_B1.offset, op_B2.offset,
            #   0, 1                            // 0 means op_B1 is in dynamic_buffer, and 1 means op_B2 is in static_buffer
            # };

        """
        if self.offset_map is None:
            self._generate_buffer()

        if tag.name == "META_BUFFER":
            return self.meta_name

        elif tag.name == "STATIC_BUFFER":
            return self.static_name

        elif tag.name == "DYNAMIC_BUFFER":
            return self.dynamic_name

        elif tag.name == "LOAD_BUFFER":
            if len(tag.args) == 0:
                raise ValueError(f"BufferInjector requires more than 1 arguments: {tag.original}")

            key = tag.args[0]
            if key not in self.value_map:
                raise KeyError(f"key '{key}' is not registered in BufferInjector.")

            value = self.value_map[key]

            if isinstance(value, Allocation):
                if len(tag.args) > 2:
                    warnings.warn(f"BufferInjector requires only 1 arguments to inject: {tag.original}")

                if value.buffer_type == BufferType.Static:
                    return f"({self.static_name} + {self.meta_name}[{self.offset_map[key]}])"

                else:
                    return f"({self.dynamic_name} + {self.meta_name}[{self.offset_map[key]}])"

            if isinstance(value, List):

                value = _flatten(value)

                if all([isinstance(a, Allocation) for a in value]):
                    if len(tag.args) < 2:
                        raise ValueError(f"Second argument 'Index' is required to inject a list of allocations: {tag.original}")

                    if len(tag.args) > 2:
                        warnings.warn(f"BufferInjector requires only 2 arguments to inject a list of allocations: {tag.original}")

                    index = tag.args[1]
                    return f"({self.meta_name}[{self.offset_map[key]}+{len(value)}+ ({index})] ? {self.static_name} : {self.dynamic_name})" + \
                           f"[{self.meta_name}[{self.offset_map[key]} + ({index})]]"

            if len(tag.args) > 2:
                warnings.warn(f"BufferInjector requires only 1 arguments to inject: {tag.original}")

            return f"{self.meta_name}[{self.offset_map[key]}]"

        else:
            return tag.original

    def _generate_buffer(self) -> bytes:
        if self.buffer:
            return self.buffer

        offset_map = {}
        buffer = bytes()
        for key, value in self.value_map.items():
            offset_map[key] = len(buffer) // 4  # sizeof(int)

            if isinstance(value, int) or isinstance(value, np.int32) or isinstance(value, np.int64):
                if isinstance(value, np.int64):
                    warnings.warn("np.int64 value is given to BufferInjector, and converted into int32 value.")

                buffer += np.array([value], dtype=np.int32).tobytes()

            elif isinstance(value, float) or isinstance(value, np.float32) or isinstance(value, np.float64):
                if isinstance(value, np.float64):
                    warnings.warn("np.float64 value is given to BufferInjector, and converted into float32 value.")

                buffer += np.array([value], dtype=np.float32).tobytes()

            elif isinstance(value, bytes):
                if len(value) % 4 != 0:
                    value += bytes(4 - (len(value) % 4))

                buffer += value

            elif isinstance(value, Allocation):
                if PlaceHolder.check_resolved(value.offset):
                    buffer += np.array([PlaceHolder.force_int(value.offset)], dtype=np.int32).tobytes()

                else:
                    self.unresolved_value_list.append((len(buffer) // 4, value.offset))
                    buffer += bytes(4)  # sizeof(int)

            elif isinstance(value, PlaceHolder):
                if PlaceHolder.check_resolved(value):
                    buffer += np.array([PlaceHolder.force_int(value)], dtype=np.int32).tobytes()

                else:
                    self.unresolved_value_list.append((len(buffer) // 4, value))
                    buffer += bytes(4)  # sizeof(int)

            elif isinstance(value, List):
                value = _flatten(value)

                if all([isinstance(p, int) or isinstance(p, PlaceHolder) for p in value]):
                    for p in value:
                        if isinstance(p, int) or isinstance(p, PlaceHolder):
                            if PlaceHolder.check_resolved(p):
                                buffer += np.array([PlaceHolder.force_int(p)], dtype=np.int32).tobytes()

                            else:
                                self.unresolved_value_list.append((len(buffer) // 4, p))
                                buffer += bytes(4)  # sizeof(int)

                elif all([isinstance(a, Allocation) for a in value]):
                    """
                    Input:

                        value = [static1, dynamic2, ..., staticK]  # allocations list whose length is K
                        tag = "float *x_i = %%LOAD_BUFFER(xs, i)%%"
                    
                    1. pack offset of each allocation into meta buffer like single allocation:

                        meta_buffer[M + 0]   = static1.offset
                        meta_buffer[M + 1]   = dynamic2.offset // In compile-time, this value is 0
                        ...
                        meta_buffer[M + K-1] = staticK.offset

                    2. pack buffer type flag:

                        meta_buffer[M + K + 0]   = 1  // static1 is in static buffer 
                        meta_buffer[M + K + 1]   = 0  // dynamic2 is not in static buffer
                        ...
                        meta_buffer[M + K + K-1] = 0
                        
                    3. generate text:

                        >> "float *x_i = (meta_buffer[M+K+ (i)] ? static_buffer : dynamic_buffer)[ meta_buffer[M + (i)] ]"

                    """

                    for allocation in value:  # type: Allocation
                        if PlaceHolder.check_resolved(allocation.offset):
                            buffer += np.array([PlaceHolder.force_int(allocation.offset)], dtype=np.int32).tobytes()

                        else:
                            self.unresolved_value_list.append((len(buffer) // 4, allocation.offset))
                            buffer += bytes(4)  # sizeof(int)

                    buffer += np.array([1 if allocation.buffer_type == BufferType.Static else 0 for allocation in value],
                                       dtype=np.int32).tobytes()

            else:
                raise TypeError(
                    "BufferInjector supports only int, float, bytes, allocation, placeholder and list of placeholders. " +
                    f"'{key}' is {value}, whose type is {type(value)}.")

        self.offset_map = offset_map
        self.buffer = buffer

        return self.buffer
