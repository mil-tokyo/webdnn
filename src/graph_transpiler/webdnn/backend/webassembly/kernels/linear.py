from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.code_generator.injectors.buffer_injector import BufferInjector
from webdnn.backend.webassembly.kernel import Kernel
from webdnn.graph.axis import Axis
from webdnn.graph.operators.linear import Linear
from webdnn.graph.order import OrderNC, OrderNHWC, OrderCN, OrderHWCN

template = """
void %%FUNC_NAME%%(const int * %%META_BUFFER%%)
{
    const float *X = %%LOAD_BUFFER(linear_X)%%;
    float *Y = %%LOAD_BUFFER(linear_Y)%%;
    const float *W = %%LOAD_BUFFER(linear_W)%%;
    const int M = %%LOAD_BUFFER(linear_M)%%;
    const int N = %%LOAD_BUFFER(linear_N)%%;
    const int K = %%LOAD_BUFFER(linear_K)%%;
    
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

    buffer_injector = BufferInjector()
    buffer_injector.register({
        "linear_X": x,
        "linear_Y": y,
        "linear_W": w,
        "linear_M": y.variable.shape_dict[Axis.N],
        "linear_N": y.variable.size // y.variable.shape_dict[Axis.N],
        "linear_K": x.variable.size // x.variable.shape_dict[Axis.N],
    })

    name_injector = KernelNameInjector(op)

    source = template
    source = buffer_injector.inject(source)
    source = name_injector.inject(source)

    kernel = Kernel(
        {name_injector.name: source},
        name_injector.name,
        buffer_injector.buffer,
        buffer_injector.unresolved_value_list
    )

    return [kernel]
