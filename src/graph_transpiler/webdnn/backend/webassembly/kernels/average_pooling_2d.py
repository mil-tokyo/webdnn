from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.buffer_injector import BufferInjector
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webassembly.kernel import Kernel
from webdnn.graph.axis import Axis
from webdnn.graph.operators.average_pooling_2d import AveragePooling2D
from webdnn.graph.order import OrderNHWC

template = """
void %%FUNC_NAME%%(const int * %%META_BUFFER%%)
{
    const float *X = %%LOAD_BUFFER(average_pooling_2d_X)%%;
    float *Y = %%LOAD_BUFFER(average_pooling_2d_Y)%%;
    const int N = %%LOAD_BUFFER(average_pooling_2d_N)%%;
    const int H1 = %%LOAD_BUFFER(average_pooling_2d_H1)%%;
    const int W1 = %%LOAD_BUFFER(average_pooling_2d_W1)%%;
    const int C = %%LOAD_BUFFER(average_pooling_2d_C)%%;
    const int H2 = %%LOAD_BUFFER(average_pooling_2d_H2)%%;
    const int W2 = %%LOAD_BUFFER(average_pooling_2d_W2)%%;
    
    const int KH = %%LOAD_BUFFER(average_pooling_2d_KH)%%;
    const int KW = %%LOAD_BUFFER(average_pooling_2d_KW)%%;
    const int SH = %%LOAD_BUFFER(average_pooling_2d_SH)%%;
    const int SW = %%LOAD_BUFFER(average_pooling_2d_SW)%%;
    const int PH = %%LOAD_BUFFER(average_pooling_2d_PH)%%;
    const int PW = %%LOAD_BUFFER(average_pooling_2d_PW)%%;
    
    for (int gid = 0; gid < N * H2 * W2 * C; gid += 1) {
        const int c = gid % C;
        const int w2 = gid / C % W2;
        const int h2 = gid / C / W2 % H2;
        const int n = gid / C / W2 / H2;

        float v = 0;
        for (int kh = 0; kh < KH; kh++) {
            const int h1 = h2 * SH - PH + kh;
            if (h1 < 0 || h1 >= H1) continue;
            
            for (int kw = 0; kw < KW; kw++) {
                const int w1 = w2 * SW - PW + kw;
                if (w1 < 0 || w1 >= W1) continue;

                v += X[((n * H1 + h1) * W1 + w1) * C + c];
            }
        }
        v /= KH * KW;

        Y[gid] = v;
    }
}
"""


# noinspection PyUnusedLocal
def average_pooling_2d(op: AveragePooling2D, memory_layout: MemoryLayout) -> List[Kernel]:
    x = memory_layout[op.inputs["x"]]
    y = memory_layout[op.outputs["y"]]

    assert x.variable.order == OrderNHWC
    assert y.variable.order == OrderNHWC

    buffer_injector = BufferInjector()
    buffer_injector.register({
        "average_pooling_2d_X": x,
        "average_pooling_2d_Y": y,
        "average_pooling_2d_N": x.variable.shape_dict[Axis.N],
        "average_pooling_2d_H1": x.variable.shape_dict[Axis.H],
        "average_pooling_2d_W1": x.variable.shape_dict[Axis.W],
        "average_pooling_2d_C": x.variable.shape_dict[Axis.C],
        "average_pooling_2d_H2": y.variable.shape_dict[Axis.H],
        "average_pooling_2d_W2": y.variable.shape_dict[Axis.W],
        "average_pooling_2d_KH": op.parameters["ksize"][0],
        "average_pooling_2d_KW": op.parameters["ksize"][1],
        "average_pooling_2d_SH": op.parameters["stride"][0],
        "average_pooling_2d_SW": op.parameters["stride"][1],
        "average_pooling_2d_PH": op.parameters["padding"][0],
        "average_pooling_2d_PW": op.parameters["padding"][1],
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
