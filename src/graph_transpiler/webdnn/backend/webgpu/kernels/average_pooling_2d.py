from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.code_generator.injectors.meta_injector import MetaInjector
from webdnn.backend.webgpu.kernel import Kernel, GPUSize
from webdnn.graph.axis import Axis
from webdnn.graph.operators.average_pooling_2d import AveragePooling2D
from webdnn.graph.order import OrderNHWC

template = """
kernel void %%FUNC_NAME%%(device float *data_buffer[[buffer(0)]],
                          const device int * %%META_NAME%% [[buffer(1)]],
                          uint index[[thread_position_in_grid]],
                          uint num_threads[[threads_per_grid]])
{
    const device float *X = data_buffer + %%META_LOAD(average_pooling_2d_X_offset)%%;
    device float *Y = data_buffer + %%META_LOAD(average_pooling_2d_Y_offset)%%;
    const int N = %%META_LOAD(average_pooling_2d_N)%%;
    const int H1 = %%META_LOAD(average_pooling_2d_H1)%%;
    const int W1 = %%META_LOAD(average_pooling_2d_W1)%%;
    const int C = %%META_LOAD(average_pooling_2d_C)%%;
    const int H2 = %%META_LOAD(average_pooling_2d_H2)%%;
    const int W2 = %%META_LOAD(average_pooling_2d_W2)%%;
    const int K = %%META_LOAD(average_pooling_2d_K)%%;
    const int S = %%META_LOAD(average_pooling_2d_S)%%;
    const int P = %%META_LOAD(average_pooling_2d_P)%%;
    
    for (int gid = index; gid < N * H2 * W2 * C; gid += num_threads) {
        const int c = gid % C;
        const int w2 = gid / C % W2;
        const int h2 = gid / C / W2 % H2;
        const int n = gid / C / W2 / H2;

        float v = 0;
        for (int kh = 0; kh < K; kh++) {
            const int h1 = h2 * S - P + kh;
            if (h1 < 0 || h1 >= H1) continue;
            
            for (int kw = 0; kw < K; kw++) {
                const int w1 = w2 * S - P + kw;
                if (w1 < 0 || w1 >= W1) continue;

                v += X[((n * H1 + h1) * W1 + w1) * C + c];
            }
        }
        v /= K * K;

        Y[gid] = v;
    }
}
"""


def average_pooling_2d(op: AveragePooling2D,
                       memory_layout: MemoryLayout) -> List[Kernel]:
    x = memory_layout[op.inputs["x"]]
    y = memory_layout[op.outputs["y"]]

    assert x.variable.order == OrderNHWC
    assert y.variable.order == OrderNHWC

    meta_injector = MetaInjector()
    meta_injector.register({
        "average_pooling_2d_X_offset": x.offset,
        "average_pooling_2d_Y_offset": y.offset,
        "average_pooling_2d_N": x.variable.shape_dict[Axis.N],
        "average_pooling_2d_H1": x.variable.shape_dict[Axis.H],
        "average_pooling_2d_W1": x.variable.shape_dict[Axis.W],
        "average_pooling_2d_C": x.variable.shape_dict[Axis.C],
        "average_pooling_2d_H2": y.variable.shape_dict[Axis.H],
        "average_pooling_2d_W2": y.variable.shape_dict[Axis.W],
        "average_pooling_2d_K": op.parameters["ksize"][0],
        "average_pooling_2d_S": op.parameters["stride"][0],
        "average_pooling_2d_P": op.parameters["padding"][0],
    })

    name_injector = KernelNameInjector(op)

    source = template
    source = meta_injector.inject(source)
    source = name_injector.inject(source)

    kernel = Kernel(
        {name_injector.name: source},
        name_injector.name,
        GPUSize(8, 1, 1),
        GPUSize(1024, 1, 1),
        meta_injector.buffer,
        meta_injector.unresolved_value_list
    )

    return [kernel]
