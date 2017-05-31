from typing import List

import numpy as np

from webdnn.backend.webgpu.allocator import MemoryLayout
from webdnn.backend.webgpu.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgpu.injectors.meta_injector import MetaInjector
from webdnn.backend.webgpu.kernel import GPUSize, Kernel
from webdnn.graph.operators.concat import Concat

template = """
kernel void %%FUNC_NAME%%(const device float *weight_buffer[[buffer(0)]],
                          device float *data_buffer[[buffer(1)]],
                          const device int * %%META_NAME%% [[buffer(2)]],
                          uint index[[thread_position_in_grid]],
                          uint num_threads[[threads_per_grid]])
{
    device float *y = data_buffer + %%META_LOAD(concat_y_offset)%%;
    const int N = %%META_LOAD(concat_N)%%;
    const device int *x_offsets = &(%%META_LOAD(concat_x_offsets)%%);
    const device int *x_sizes = &(%%META_LOAD(concat_x_sizes)%%);

    int n = 0;
    int x_offset = index;
    int y_offset = index;
    device float *xn = data_buffer + x_offsets[n];
    int size = x_sizes[n];
    
    while (n < N) {
        if (x_offset >= size) {
            x_offset -= size;
            n++;
            xn = data_buffer + x_offsets[n];
            size = x_sizes[n];
            continue;
        }
            
        y[y_offset] = xn[x_offset];
        
        x_offset += num_threads;
        y_offset += num_threads;
    }
}
"""


# noinspection PyUnusedLocal
def concat(op: Concat,
           constants_layout: MemoryLayout,
           variables_layout: MemoryLayout) -> List[Kernel]:
    xs = [variables_layout[op.inputs[f"x{str(i)}"]] for i in range(len(op.inputs))]
    y = variables_layout[op.outputs["y"]]
    axis = op.axis

    assert y.variable.order.axes[0] == axis, "WebGPU backend currently supports only major-axis concat."
    for x in xs:
        assert x.variable.shape[1:] == y.variable.shape[1:]

    meta_injector = MetaInjector()
    meta_injector.register({
        "concat_y_offset": y.offset,
        "concat_N": len(xs),
        "concat_x_offsets": np.array([x.offset for x in xs], dtype=np.int32).tobytes(),
        "concat_x_sizes": np.array([x.size for x in xs], dtype=np.int32).tobytes(),
    })

    name_injector = KernelNameInjector(op)

    source = template
    source = meta_injector.inject(source)
    source = name_injector.inject(source)

    kernel = Kernel(
        {name_injector.name: source},
        name_injector.name,
        GPUSize(8, 1, 1),
        GPUSize(1024, 1, 1),
        meta_injector.buffer
    )

    return [kernel]
