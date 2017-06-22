from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.code_generator.injectors.buffer_injector import BufferInjector
from webdnn.backend.webassembly.kernel import Kernel
from webdnn.graph.axis import Axis
from webdnn.graph.operators.max_pooling_2d import MaxPooling2D
from webdnn.graph.order import OrderNHWC

template = """
void %%FUNC_NAME%%(const int * %%META_BUFFER%%)
{
    const float *X = %%LOAD_BUFFER(max_pooling_2d_X)%%;
    float *Y = %%LOAD_BUFFER(max_pooling_2d_Y)%%;
    const int N = %%LOAD_BUFFER(max_pooling_2d_N)%%;
    const int H1 = %%LOAD_BUFFER(max_pooling_2d_H1)%%;
    const int W1 = %%LOAD_BUFFER(max_pooling_2d_W1)%%;
    const int C = %%LOAD_BUFFER(max_pooling_2d_C)%%;
    const int H2 = %%LOAD_BUFFER(max_pooling_2d_H2)%%;
    const int W2 = %%LOAD_BUFFER(max_pooling_2d_W2)%%;
    const int K = %%LOAD_BUFFER(max_pooling_2d_K)%%;
    const int S = %%LOAD_BUFFER(max_pooling_2d_S)%%;
    const int P = %%LOAD_BUFFER(max_pooling_2d_P)%%;

    for (int gid = 0; gid < N * H2 * W2 * C; gid += 1) {
        const int c = gid % C;
        const int w2 = gid / C % W2;
        const int h2 = gid / C / W2 % H2;
        const int n = gid / C / W2 / H2;

        float v = -1e7;
        for (int kh = 0; kh < K; kh++) {
            const int h1 = h2 * S - P + kh;
            if (h1 < 0 || h1 >= H1) continue;
            
            for (int kw = 0; kw < K; kw++) {
                const int w1 = w2 * S - P + kw;
                if (w1 < 0 || w1 >= W1) continue;

                v = v > X[((n * H1 + h1) * W1 + w1) * C + c] ? v : X[((n * H1 + h1) * W1 + w1) * C + c];
            }
        }

        Y[gid] = v;
    }
}
"""


# noinspection PyUnusedLocal
def max_pooling_2d(op: MaxPooling2D, memory_layout: MemoryLayout) -> List[Kernel]:
    x = memory_layout[op.inputs["x"]]
    y = memory_layout[op.outputs["y"]]

    assert x.variable.order == OrderNHWC
    assert y.variable.order == OrderNHWC

    buffer_injector = BufferInjector()
    buffer_injector.register({
        "max_pooling_2d_X": x,
        "max_pooling_2d_Y": y,
        "max_pooling_2d_N": x.variable.shape_dict[Axis.N],
        "max_pooling_2d_H1": x.variable.shape_dict[Axis.H],
        "max_pooling_2d_W1": x.variable.shape_dict[Axis.W],
        "max_pooling_2d_C": x.variable.shape_dict[Axis.C],
        "max_pooling_2d_H2": y.variable.shape_dict[Axis.H],
        "max_pooling_2d_W2": y.variable.shape_dict[Axis.W],
        "max_pooling_2d_K": op.parameters["ksize"][0],
        "max_pooling_2d_S": op.parameters["stride"][0],
        "max_pooling_2d_P": op.parameters["padding"][0],
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
