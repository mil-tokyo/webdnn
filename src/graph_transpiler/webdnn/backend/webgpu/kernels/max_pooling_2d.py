from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.buffer_injector import BufferInjector
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgpu.generator import WebGPUDescriptorGenerator
from webdnn.backend.webgpu.kernel import Kernel, GPUSize
from webdnn.backend.webgpu.preset_placeholders import MAX_THREADS_PER_THREADGROUP
from webdnn.graph.axis import Axis
from webdnn.graph.operators.max_pooling_2d import MaxPooling2D
from webdnn.graph.order import OrderNHWC

template = """
kernel void %%FUNC_NAME%%(device float * %%STATIC_BUFFER%%[[buffer(0)]],
                          device float * %%DYNAMIC_BUFFER%%[[buffer(1)]],
                          const device int * %%META_BUFFER%% [[buffer(2)]],
                          uint index[[thread_position_in_grid]],
                          uint num_threads[[threads_per_grid]])
{
    const device float *X = %%LOAD_BUFFER(max_pooling_2d_X)%%;
    device float *Y = %%LOAD_BUFFER(max_pooling_2d_Y)%%;
    const int N = %%LOAD_BUFFER(max_pooling_2d_N)%%;
    const int H1 = %%LOAD_BUFFER(max_pooling_2d_H1)%%;
    const int W1 = %%LOAD_BUFFER(max_pooling_2d_W1)%%;
    const int C = %%LOAD_BUFFER(max_pooling_2d_C)%%;
    const int H2 = %%LOAD_BUFFER(max_pooling_2d_H2)%%;
    const int W2 = %%LOAD_BUFFER(max_pooling_2d_W2)%%;

    const int KH = %%LOAD_BUFFER(max_pooling_2d_KH)%%;
    const int KW = %%LOAD_BUFFER(max_pooling_2d_KW)%%;
    const int SH = %%LOAD_BUFFER(max_pooling_2d_SH)%%;
    const int SW = %%LOAD_BUFFER(max_pooling_2d_SW)%%;
    const int PH = %%LOAD_BUFFER(max_pooling_2d_PH)%%;
    const int PW = %%LOAD_BUFFER(max_pooling_2d_PW)%%;

    for (int gid = index; gid < N * H2 * W2 * C; gid += num_threads) {
        const int c = gid % C;
        const int w2 = gid / C % W2;
        const int h2 = gid / C / W2 % H2;
        const int n = gid / C / W2 / H2;

        float v = -1e7;
        for (int kh = 0; kh < KH; kh++) {
            const int h1 = h2 * SH - PH + kh;
            if (h1 < 0 || h1 >= H1) continue;

            for (int kw = 0; kw < KW; kw++) {
                const int w1 = w2 * SW - PW + kw;
                if (w1 < 0 || w1 >= W1) continue;

                v = v > X[((n * H1 + h1) * W1 + w1) * C + c] ? v : X[((n * H1 + h1) * W1 + w1) * C + c];
            }
        }

        Y[gid] = v;
    }
}
"""


@WebGPUDescriptorGenerator.register_handler(MaxPooling2D)
def max_pooling_2d(op: MaxPooling2D, memory_layout: MemoryLayout) -> List[Kernel]:
    x = op.inputs["x"]
    y = op.outputs["y"]

    assert x.order == OrderNHWC
    assert y.order == OrderNHWC

    buffer_injector = BufferInjector()
    buffer_injector.register({
        "max_pooling_2d_X": memory_layout[x],
        "max_pooling_2d_Y": memory_layout[y],
        "max_pooling_2d_N": x.shape_dict[Axis.N],
        "max_pooling_2d_H1": x.shape_dict[Axis.H],
        "max_pooling_2d_W1": x.shape_dict[Axis.W],
        "max_pooling_2d_C": x.shape_dict[Axis.C],
        "max_pooling_2d_H2": y.shape_dict[Axis.H],
        "max_pooling_2d_W2": y.shape_dict[Axis.W],
        "max_pooling_2d_KH": op.parameters["ksize"][0],
        "max_pooling_2d_KW": op.parameters["ksize"][1],
        "max_pooling_2d_SH": op.parameters["stride"][0],
        "max_pooling_2d_SW": op.parameters["stride"][1],
        "max_pooling_2d_PH": op.parameters["padding"][0],
        "max_pooling_2d_PW": op.parameters["padding"][1],
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
