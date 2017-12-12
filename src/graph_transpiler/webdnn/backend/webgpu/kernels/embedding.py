from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.buffer_injector import BufferInjector
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgpu.generator import WebGPUDescriptorGenerator
from webdnn.backend.webgpu.kernel import Kernel, GPUSize
from webdnn.backend.webgpu.preset_placeholders import MAX_THREADS_PER_THREADGROUP
from webdnn.graph.axis import Axis
from webdnn.graph.operators.embedding import Embedding
from webdnn.graph.order import OrderCN, OrderNT, OrderNTC

template = """
kernel void %%FUNC_NAME%%(device float * %%STATIC_BUFFER%%[[buffer(0)]],
                          device float * %%DYNAMIC_BUFFER%%[[buffer(1)]],
                          const device int * %%META_BUFFER%% [[buffer(2)]],
                          uint global_index[[thread_position_in_grid]],
                          uint num_threads[[threads_per_grid]])
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


@WebGPUDescriptorGenerator.register_handler(Embedding)
def embedding(op: Embedding, memory_layout: MemoryLayout) -> List[Kernel]:
    x = op.inputs["x"]
    w = op.inputs["w"]
    y = op.outputs["y"]

    assert x.order == OrderNT
    assert w.order == OrderCN
    assert y.order == OrderNTC

    buffer_injector = BufferInjector()
    buffer_injector.register({
        "embedding_X": memory_layout[x],
        "embedding_Y": memory_layout[y],
        "embedding_W": memory_layout[w],
        "embedding_T": x.shape_dict[Axis.T],
        "embedding_N": x.shape_dict[Axis.N],
        "embedding_C": w.shape_dict[Axis.N]
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
