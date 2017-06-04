from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.code_generator.injectors.meta_injector import MetaInjector
from webdnn.backend.webassembly.kernel import Kernel
from webdnn.graph.axis import Axis
from webdnn.graph.operators.linear import Linear
from webdnn.graph.order import OrderNC, OrderNHWC, OrderCN, OrderHWCN

template = """
void %%FUNC_NAME%%(const int * %%META_NAME%%)
{
    const float *X = data_buffer + %%META_LOAD(linear_X_offset)%%;
    float *Y = data_buffer + %%META_LOAD(linear_Y_offset)%%;
    const float *W = data_buffer + %%META_LOAD(linear_W_offset)%%;
    const int M = %%META_LOAD(linear_M)%%;
    const int N = %%META_LOAD(linear_N)%%;
    const int K = %%META_LOAD(linear_K)%%;
    
    for (int gid = 0; gid < M * N; gid += 1) {
        int n = gid % N;
        int m = gid / N;

        float sum = 0.0;
        for (int k = 0; k < K; k++) {
            sum += X[m * K + k] * W[k * N + n];
        }

        Y[gid] = sum;
    }
}
"""


def linear(op: Linear, memory_layout: MemoryLayout) -> List[Kernel]:
    x = memory_layout[op.inputs["x"]]
    w = memory_layout[op.inputs["w"]]
    y = memory_layout[op.outputs["y"]]

    assert x.variable.order == OrderNC or x.variable.order == OrderNHWC
    assert w.variable.order == OrderCN or w.variable.order == OrderHWCN
    assert y.variable.order == OrderNC or y.variable.order == OrderNHWC
    assert w.variable.ndim == x.variable.ndim

    meta_injector = MetaInjector()
    meta_injector.register({
        "linear_X_offset": x.offset,
        "linear_Y_offset": y.offset,
        "linear_W_offset": w.offset,
        "linear_M": y.variable.shape_dict[Axis.N],
        "linear_N": y.variable.size // y.variable.shape_dict[Axis.N],
        "linear_K": x.variable.size // x.variable.shape_dict[Axis.N],
    })

    name_injector = KernelNameInjector(op)

    source = template
    source = meta_injector.inject(source)
    source = name_injector.inject(source)

    kernel = Kernel(
        {name_injector.name: source},
        name_injector.name,
        meta_injector.buffer
    )

    return [kernel]
