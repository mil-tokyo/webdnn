from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.buffer_injector import BufferInjector
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webassembly.generator import WebassemblyDescriptorGenerator
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


@WebassemblyDescriptorGenerator.register_handler(Linear)
def linear(op: Linear, memory_layout: MemoryLayout) -> List[Kernel]:
    x = op.inputs["x"]
    w = op.inputs["w"]
    y = op.outputs["y"]

    assert x.order == OrderNC or x.order == OrderNHWC
    assert w.order == OrderCN or w.order == OrderHWCN
    assert y.order == OrderNC or y.order == OrderNHWC
    assert w.ndim == x.ndim

    buffer_injector = BufferInjector()
    buffer_injector.register({
        "linear_X": memory_layout[x],
        "linear_Y": memory_layout[y],
        "linear_W": memory_layout[w],
        "linear_M": y.shape_dict[Axis.N],
        "linear_N": y.size // y.shape_dict[Axis.N],
        "linear_K": x.size // x.shape_dict[Axis.N],
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
