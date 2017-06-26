from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.buffer_injector import BufferInjector
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgpu.kernel import Kernel, GPUSize
from webdnn.backend.webgpu.preset_placeholders import MAX_THREADS_PER_THREADGROUP
from webdnn.graph.axis import Axis
from webdnn.graph.operators.embedding import Embedding
from webdnn.graph.order import OrderCN, OrderNT, OrderNTC

template = """
kernel void %%FUNC_NAME%%(device float * %%STATIC_BUFFER%%[[buffer(0)]],
                          device float * %%DYNAMIC_BUFFER%%[[buffer(1)]],
                          const device int * %%META_BUFFER%% [[buffer(2)]],
                          ushort global_index[[thread_position_in_grid]],
                          ushort num_threads[[threads_per_grid]])
{
    const device float *X = %%LOAD_BUFFER(embedding_X)%%;
    device float       *Y = %%LOAD_BUFFER(embedding_Y)%%;
    const device float *W = %%LOAD_BUFFER(embedding_W)%%;
    
    const int T = %%LOAD_BUFFER(embedding_T)%%;
    const int N = %%LOAD_BUFFER(embedding_N)%%;
    const int C = %%LOAD_BUFFER(embedding_C)%%;

    for (int gid = global_index; gid < N * T; gid += num_threads) {
        const int t = gid % T;
        const int n = gid / T;

        const int word = (int)X[gid];
        for (int c = 0; c < C; c++) {
            Y[(n * T + t) * C + c] = W[word * C + c];
        }
    }
}
"""


def embedding(op: Embedding, memory_layout: MemoryLayout) -> List[Kernel]:
    x = memory_layout[op.inputs["x"]]
    w = memory_layout[op.inputs["w"]]
    y = memory_layout[op.outputs["y"]]

    assert x.variable.order == OrderNT
    assert w.variable.order == OrderCN
    assert y.variable.order == OrderNTC

    buffer_injector = BufferInjector()
    buffer_injector.register({
        "embedding_X": x,
        "embedding_Y": y,
        "embedding_W": w,
        "embedding_T": x.variable.shape_dict[Axis.T],
        "embedding_N": x.variable.shape_dict[Axis.N],
        "embedding_C": w.variable.shape_dict[Axis.N]
    })

    name_injector = KernelNameInjector(op)

    source = template
    source = buffer_injector.inject(source)
    source = name_injector.inject(source)

    kernel = Kernel(
        {name_injector.name: source},
        name_injector.name,
        GPUSize(8, 1, 1),
        GPUSize(MAX_THREADS_PER_THREADGROUP, 1, 1),
        buffer_injector.buffer,
        buffer_injector.unresolved_value_list
    )

    return [kernel]
