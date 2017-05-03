from collections import OrderedDict
from typing import Iterable, Dict
import numpy as np

from graph_builder.backend.webassembly.allocator import MemoryLayout
from graph_builder.backend.webassembly.kernel import Kernel
from graph_builder.graph.variable import Variable
from graph_builder.graph.variables.attributes.constant import Constant
from graph_builder.optimize_rule import util
from graph_builder.util import json

source_header = """
#include <stdlib.h>

float weight_buffer[%%WEIGHT_SIZE%%];
float data_buffer[%%DATA_SIZE%%];

"""

source_init = """
void init() {
    //weight_buffer = (float*)malloc(%%WEIGHT_SIZE%% * sizeof(float));
    //data_buffer = (float*)malloc(%%DATA_SIZE%% * sizeof(float));
}

float* get_weight_buffer(void) {
    return weight_buffer;
}

float* get_data_buffer(void) {
    return data_buffer;
}

"""

source_exec = """
void run() {
%%EXEC_LINES%%
}

"""


class GraphDescriptor(json.SerializableMixin):
    kernels: Iterable[Kernel]
    constants_layout: MemoryLayout
    variables_layout: MemoryLayout
    inputs: Iterable[Variable]
    outputs: Iterable[Variable]
    constants_encoding: str
    footer_sources: Dict[str, str]

    def __init__(self,
                 kernels: Iterable[Kernel],
                 constants_layout: MemoryLayout,
                 variables_layout: MemoryLayout,
                 inputs: Iterable[Variable],
                 outputs: Iterable[Variable],
                 constants_encoding: str):
        self.kernels = kernels
        self.constants_layout = constants_layout
        self.variables_layout = variables_layout
        self.inputs = inputs
        self.outputs = outputs
        self.constants_encoding = constants_encoding
        self.footer_sources = OrderedDict()

    def generate_header_source(self):
        return source_header \
            .replace("%%WEIGHT_SIZE%%", str(self.constants_layout.size)) \
            .replace("%%DATA_SIZE%%", str(self.variables_layout.size))

    def generate_init_source(self):
        self.footer_sources["init"] = source_init \
            .replace("%%WEIGHT_SIZE%%", str(self.constants_layout.size)) \
            .replace("%%DATA_SIZE%%", str(self.variables_layout.size))

    def generate_exec_line(self, kernel: Kernel, serial: int):
        line = f"const int meta_buf_{serial}[] = {{"
        # see as int32 and convert to 12345,67890
        line += ",".join(map(str, np.fromstring(kernel.exec_info.meta_buffer, dtype=np.int32).tolist()))
        line += "};\n"
        line += f"{kernel.exec_info.entry_func_name}(meta_buf_{serial});\n"
        return line

    def generate_exec_source(self):
        lines = ""
        for serial, kernel in enumerate(self.kernels):
            lines += self.generate_exec_line(kernel, serial)
        self.footer_sources["exec"] = source_exec.replace("%%EXEC_LINES%%", lines)

    def concat_kernel_sources(self):
        func_sources = OrderedDict()
        prototype_sources = OrderedDict()

        for kernel in self.kernels:
            for func_name, source in kernel.func_sources.items():
                if func_name in func_sources:
                    assert func_sources[func_name] == source
                else:
                    func_sources[func_name] = source

            for func_name, source in kernel.prototype_sources.items():
                if func_name in prototype_sources:
                    assert prototype_sources[func_name] == source
                else:
                    prototype_sources[func_name] = source

        self.generate_init_source()
        self.generate_exec_source()
        combined_source = \
            self.generate_header_source() + \
            "\n".join(prototype_sources.values()) + \
            "\n".join(func_sources.values()) + \
            "\n".join(self.footer_sources.values())

        return combined_source

    def _to_serializable_(self):
        return {
            "weight_allocation": self.constants_layout,
            "weight_encoding": self.constants_encoding,
            "variable_allocation": self.variables_layout,
            "inputs": [v.parameters["name"] for v in self.inputs if not util.check_attribute_match(v, Constant)],
            "outputs": [v.parameters["name"] for v in self.outputs],
            "entry_js_path": "./output/kernels_webassembly.js"  # TODO: not set here
        }
