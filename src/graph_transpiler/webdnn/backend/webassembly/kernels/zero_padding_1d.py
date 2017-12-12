from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.buffer_injector import BufferInjector
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webassembly.generator import WebassemblyDescriptorGenerator
from webdnn.backend.webassembly.kernel import Kernel
from webdnn.graph.axis import Axis
from webdnn.graph.operators.zero_padding_1d import ZeroPadding1D
from webdnn.graph.order import OrderNTC

template = """
void %%FUNC_NAME%%(const int * %%META_BUFFER%%)
{
    const float *X = %%LOAD_BUFFER(zero_padding_1d_X)%%;
    float *Y = %%LOAD_BUFFER(zero_padding_1d_Y)%%;
    const int N = %%LOAD_BUFFER(zero_padding_1d_N)%%;
    const int T1 = %%LOAD_BUFFER(zero_padding_1d_T1)%%;
    const int C = %%LOAD_BUFFER(zero_padding_1d_C)%%;
    const int T2 = %%LOAD_BUFFER(zero_padding_1d_T2)%%;
    const int Pad1L = %%LOAD_BUFFER(zero_padding_1d_Pad1L)%%;

    for (int gid = 0; gid < N * T2 * C; gid += 1) {
        const int c = gid % C;
        const int t2 = gid / C % T2;
        const int n = gid / C / T2;

        const int t1 = t2 - Pad1L;
        float v = 0.0F;
        if ((t1 >= 0) && (t1 < T1)) {
            v = X[(n * T1 + t1) * C + c];
        }

        Y[gid] = v;
    }
}
"""


@WebassemblyDescriptorGenerator.register_handler(ZeroPadding1D)
def zero_padding_1d(op: ZeroPadding1D, memory_layout: MemoryLayout) -> List[Kernel]:
    x = op.inputs["x"]
    y = op.outputs["y"]

    assert x.order == OrderNTC
    assert y.order == OrderNTC

    buffer_injector = BufferInjector()
    buffer_injector.register({
        "zero_padding_1d_X": memory_layout[x],
        "zero_padding_1d_Y": memory_layout[y],
        "zero_padding_1d_N": x.shape_dict[Axis.N],
        "zero_padding_1d_T1": x.shape_dict[Axis.T],
        "zero_padding_1d_C": x.shape_dict[Axis.C],
        "zero_padding_1d_T2": y.shape_dict[Axis.T],
        "zero_padding_1d_Pad1L": op.parameters["padding"][0],
    })
    # "zero_padding_1d_Pad1H": op.parameters["padding"][1] # unused in kernel

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
