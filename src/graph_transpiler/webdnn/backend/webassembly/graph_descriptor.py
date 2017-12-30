from collections import OrderedDict
from datetime import datetime
from typing import Dict, Iterable, List, Set, Tuple

import numpy as np

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.interface.graph_descriptor import IGraphDescriptor
from webdnn.backend.webassembly.kernel import Kernel
from webdnn.graph.placeholder import Placeholder
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable
from webdnn.util import json

source_header = """
#include <stdlib.h>
#include <math.h>

float static_buffer[%%STATIC_SIZE%%];
float* dynamic_buffer = nullptr;

"""

source_init = """
extern "C" void init() {
    //static_buffer = (float*)malloc(%%STATIC_SIZE%% * sizeof(float));
}

extern "C" float* get_static_buffer(void) {
    return static_buffer;
}

extern "C" float* allocate_dynamic_buffer(int count) {
    if (dynamic_buffer) {
        free(dynamic_buffer);
        dynamic_buffer = nullptr;
    }
    dynamic_buffer = (float*)malloc(count * sizeof(float));
    return dynamic_buffer;
}

extern "C" float* get_dynamic_buffer(void) {
    return dynamic_buffer;
}
extern "C" void set_placeholder_value(int kernel_order, int offset, int value) {
    meta_buffers[kernel_order][offset] = value;
}
"""

source_exec = """
extern "C" void run() {
%%EXEC_LINES%%
}

"""


class GraphDescriptor(json.SerializableMixin, IGraphDescriptor):
    kernels: List[Kernel]
    memory_layout: MemoryLayout
    inputs: Iterable[Variable]
    outputs: Iterable[Variable]
    constants_encoding: str
    header_sources: Dict[str, str]
    footer_sources: Dict[str, str]
    required_heap: int
    licenses: Dict[str, str]

    def __init__(self,
                 kernels: List[Kernel],
                 memory_layout: MemoryLayout,
                 inputs: Iterable[Variable],
                 outputs: Iterable[Variable],
                 constants_encoding: str,
                 required_heap: int,
                 licenses: Dict[str, str]):
        self.kernels = kernels
        self.memory_layout = memory_layout
        self.inputs = inputs
        self.outputs = outputs
        self.constants_encoding = constants_encoding
        self.header_sources = OrderedDict()
        self.footer_sources = OrderedDict()
        self.required_heap = required_heap
        self.licenses = licenses

    def generate_top_source(self):
        self.header_sources["top"] = source_header \
            .replace("%%STATIC_SIZE%%", str(self.memory_layout.static_size))

    def generate_init_source(self):
        self.header_sources["init"] = source_init \
            .replace("%%STATIC_SIZE%%", str(self.memory_layout.static_size))

    # noinspection PyMethodMayBeStatic
    def generate_exec_line(self, kernel: Kernel, serial: int):
        line = f"{kernel.exec_info.entry_func_name}(meta_buf_{serial});\n"
        return line

    # noinspection PyMethodMayBeStatic
    def generate_kernel_metabuffer_initializer_line(self, kernel: Kernel, serial: int):
        line = "int meta_buf_" + str(serial) + "[] = {"
        # see as int32 and convert to 12345,67890
        # noinspection PyTypeChecker
        line += ",".join(map(str, np.fromstring(kernel.exec_info.meta_buffer, dtype=np.int32).tolist()))
        line += "};\n"
        return line

    def generate_exec_source(self):
        lines = ""
        meta_buffer_initializer = ""
        for serial, kernel in enumerate(self.kernels):
            meta_buffer_initializer += self.generate_kernel_metabuffer_initializer_line(kernel, serial)
            lines += self.generate_exec_line(kernel, serial)
        meta_buffer_initializer += "int* meta_buffers[] = {"
        meta_buffer_initializer += ",".join(["meta_buf_" + str(serial) for serial in range(len(self.kernels))])
        meta_buffer_initializer += "};\n"
        self.footer_sources["exec"] = source_exec.replace("%%EXEC_LINES%%", lines)
        self.header_sources["meta_buffer_initializer"] = meta_buffer_initializer

    def concat_kernel_sources(self):
        func_sources = OrderedDict()

        for kernel in self.kernels:
            for func_name, source in kernel.func_sources.items():
                if func_name in func_sources:
                    assert func_sources[func_name] == source
                else:
                    func_sources[func_name] = source

        self.generate_top_source()
        self.generate_exec_source()
        self.generate_init_source()
        combined_source = \
            "".join(self.header_sources.values()) + \
            "\n".join(func_sources.values()) + \
            "".join(self.footer_sources.values())

        return combined_source

    def get_all_placeholders(self):
        unresolved_variables = []  # type: List[Tuple[int, Placeholder]]
        placeholders_set = set()  # type: Set[Placeholder]

        for kernel in self.kernels:
            unresolved_variables += kernel.exec_info.unresolved_value_list

        for offset, v in unresolved_variables:
            placeholders_set.update(v.get_depend_placeholders())

        placeholders = {p.label: None for p in placeholders_set}

        return placeholders

    def _to_serializable_(self):
        placeholders = self.get_all_placeholders()
        unresolved_value_lists = []
        for kernel in self.kernels:
            unresolved_value_list = kernel.exec_info.unresolved_value_list or []
            unresolved_value_lists.append([{"offset": v[0], "placeholder": v[1]} for v in unresolved_value_list])

        return {
            "converted_at": int(datetime.timestamp(datetime.now())),
            "weight_encoding": self.constants_encoding,
            "memory_layout": self.memory_layout,
            "placeholders": placeholders,
            "unresolved_value_lists": unresolved_value_lists,
            "inputs": [self.memory_layout[v].name for v in self.inputs if not isinstance(v, ConstantVariable)],
            "outputs": [self.memory_layout[v].name for v in self.outputs],
            "licenses": self.licenses
        }
