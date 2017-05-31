from typing import List

import numpy as np

from webdnn.backend.webassembly.kernel import Kernel
from webdnn.backend.webassembly.kernels import util
from webdnn.backend.webassembly.meta_buffer_injector import MetaBufferInjector
from webdnn.backend.webgpu.allocator import MemoryLayout
from webdnn.graph.operators.concat import Concat

template = """
void %%FUNC_NAME%%(const int * %%META_NAME%%)
{
    float *y = data_buffer + %%META_LOAD(concat_y_offset)%%;
    const int N = %%META_LOAD(concat_N)%%;
    const int *x_offsets = &(%%META_LOAD(concat_x_offsets)%%);
    const int *x_sizes = &(%%META_LOAD(concat_x_sizes)%%);

    int n = 0;
    int x_offset = 0;
    int y_offset = 0;
    const float *xn = data_buffer + x_offsets[n];
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
        
        x_offset++;
        y_offset++;
    }
}
"""


# noinspection PyUnusedLocal
def concat(op: Concat,
           constants_layout: MemoryLayout,
           variables_layout: MemoryLayout,
           metabuffer_injector: MetaBufferInjector = None) -> List[Kernel]:
    xs = [variables_layout[op.inputs[f"x{str(i)}"]] for i in range(len(op.inputs))]
    y = variables_layout[op.outputs["y"]]
    axis = op.axis

    assert y.variable.order.axes[0] == axis, "WebGPU backend currently supports only major-axis concat."
    for x in xs:
        assert x.variable.shape[1:] == y.variable.shape[1:]

    if metabuffer_injector is None:
        metabuffer_injector = MetaBufferInjector()

    metabuffer_injector.register({
        "concat_y_offset": y.offset,
        "concat_N": len(xs),
        "concat_x_offsets": np.array([x.offset for x in xs], dtype=np.int32).tobytes(),
        "concat_x_sizes": np.array([x.size for x in xs], dtype=np.int32).tobytes(),
    })

    source = metabuffer_injector.inject(template)
    func_name = util.add_canonical_suffix("concat", source)
    source = source.replace("%%FUNC_NAME%%", func_name)

    kernel = Kernel(
        {func_name: source},
        func_name,
        metabuffer_injector.generate_buffer()
    )

    return [kernel]
