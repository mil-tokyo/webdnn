from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.buffer_injector import BufferInjector
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webassembly.generator import WebassemblyDescriptorGenerator
from webdnn.backend.webassembly.kernel import Kernel
from webdnn.graph.axis import Axis
from webdnn.graph.operators.depth2space import Depth2Space
from webdnn.graph.order import OrderNHWC

template = """
void %%FUNC_NAME%%(const int * %%META_BUFFER%%)
{
    const float *x = %%LOAD_BUFFER(depth2space_x)%%;
    float *y = %%LOAD_BUFFER(depth2space_y)%%;
    const int r = %%LOAD_BUFFER(depth2space_r)%%;

    const int N = %%LOAD_BUFFER(depth2space_N)%%;
    const int C1 = %%LOAD_BUFFER(depth2space_C1)%%;
    const int C2 = %%LOAD_BUFFER(depth2space_C2)%%;
    const int H1 = %%LOAD_BUFFER(depth2space_H1)%%;
    const int H2 = %%LOAD_BUFFER(depth2space_H2)%%;
    const int W1 = %%LOAD_BUFFER(depth2space_W1)%%;
    const int W2 = %%LOAD_BUFFER(depth2space_W2)%%;

    for (int gid = 0; gid < N*H2*W2*C2; gid += 1) {
        const int c2 = gid % C2;
        const int w2 = gid / C2 % W2;
        const int h2 = gid / C2 / W2 % H2;
        const int n = gid / C2 / W2 / H2;
        const int w1 = w2 / r;
        const int h1 = h2 / r;
        const int c1 = c2 + (w2 % r) * C2 + (h2 % r) * C2 * r;
        y[gid] = x[((n*H1+h1)*W1+w1)*C1+c1];
    }
}
"""


@WebassemblyDescriptorGenerator.register_handler(Depth2Space)
def depth2space(op: Depth2Space, memory_layout: MemoryLayout) -> List[Kernel]:
    x = op.inputs["x"]
    y = op.outputs["y"]
    r = op.parameters['r']

    assert x.order == OrderNHWC
    assert y.order == OrderNHWC

    buffer_injector = BufferInjector()
    buffer_injector.register({
        "depth2space_x": memory_layout[x],
        "depth2space_y": memory_layout[y],
        'depth2space_r': r,
        "depth2space_N": x.shape_dict[Axis.N],
        "depth2space_C1": x.shape_dict[Axis.C],
        "depth2space_C2": y.shape_dict[Axis.C],
        "depth2space_H1": x.shape_dict[Axis.H],
        "depth2space_H2": y.shape_dict[Axis.H],
        "depth2space_W1": x.shape_dict[Axis.W],
        "depth2space_W2": y.shape_dict[Axis.W],
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
