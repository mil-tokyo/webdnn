from typing import List

from graph_transpiler.backend.webassembly.kernel import Kernel
from graph_transpiler.backend.webassembly.kernels import util
from graph_transpiler.backend.webassembly.meta_buffer_injector import MetaBufferInjector
from graph_transpiler.backend.webgpu.allocator import MemoryLayout
from graph_transpiler.backend.webgpu.kernel import GPUSize
from graph_transpiler.graph.operators.flatten import Flatten

template = """
void %%FUNC_NAME%%(const int * %%META_NAME%% )
{
    const float *x = data_buffer + %%META_LOAD(flatten_x_offset)%%;
    float *y = data_buffer + %%META_LOAD(flatten_y_offset)%%;

    const int N = %%META_LOAD(flatten_N)%%;

    for (int gid = 0; gid < N; gid += 1) {
        y[gid] = x[gid];
    }
}
"""


def flatten(op: Flatten,
            constants_layout: MemoryLayout,
            variables_layout: MemoryLayout,
            metabuffer_injector: MetaBufferInjector = None) -> List[Kernel]:
    x = variables_layout[op.inputs["x"]]
    y = variables_layout[op.outputs["y"]]

    if metabuffer_injector is None:
        metabuffer_injector = MetaBufferInjector()

    metabuffer_injector.register({
        "flatten_x_offset": x.offset,
        "flatten_y_offset": y.offset,
        "flatten_N": y.variable.size,
    })

    source = metabuffer_injector.inject(template)
    func_name = util.add_canonical_suffix("flatten", source)
    source = source.replace("%%FUNC_NAME%%", func_name)

    kernel = Kernel(
        {func_name: source},
        func_name,
        metabuffer_injector.generate_buffer()
    )

    return [kernel]
