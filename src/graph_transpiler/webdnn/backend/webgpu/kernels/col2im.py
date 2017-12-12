from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.buffer_injector import BufferInjector
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgpu.generator import WebGPUDescriptorGenerator
from webdnn.backend.webgpu.kernel import GPUSize, Kernel
from webdnn.backend.webgpu.preset_placeholders import MAX_THREADS_PER_THREADGROUP
from webdnn.graph.axis import Axis
from webdnn.graph.operators.col2im import Col2Im
from webdnn.graph.order import OrderNHWC, Order

# NOTE
#
# "C1", "H1", and "W1" represent size of input variable of Convolution (or output variable of Deconvolution)
# "C2", "H2", and "W2" represent size of output variable of Convolution (or input variable of Deconvolution)

template = """
kernel void %%FUNC_NAME%%(device float * %%STATIC_BUFFER%%[[buffer(0)]],
                          device float * %%DYNAMIC_BUFFER%%[[buffer(1)]],
                          const device int * %%META_BUFFER%% [[buffer(2)]],
                          uint index[[thread_position_in_grid]],
                          uint num_threads[[threads_per_grid]])
{
    const device float *col = %%LOAD_BUFFER(col2im_col)%%;
    device float *im = %%LOAD_BUFFER(col2im_im)%%;

    const int N = %%LOAD_BUFFER(col2im_N)%%;
    const int C1 = %%LOAD_BUFFER(col2im_C1)%%;
    const int H1 = %%LOAD_BUFFER(col2im_H1)%%;
    const int W1 = %%LOAD_BUFFER(col2im_W1)%%;
    const int H2 = %%LOAD_BUFFER(col2im_H2)%%;
    const int W2 = %%LOAD_BUFFER(col2im_W2)%%;
    const int KH = %%LOAD_BUFFER(col2im_KH)%%;
    const int KW = %%LOAD_BUFFER(col2im_KW)%%;
    const int SH = %%LOAD_BUFFER(col2im_SH)%%;
    const int SW = %%LOAD_BUFFER(col2im_SW)%%;
    const int PH = %%LOAD_BUFFER(col2im_PH)%%;
    const int PW = %%LOAD_BUFFER(col2im_PW)%%;

    for (int gid = index; gid < N*H1*W1*C1; gid += num_threads) {
        const int c1 = gid % C1;
        const int w1 = gid / C1 % W1;
        const int h1 = gid / C1 / W1 % H1;
        const int n  = gid / C1 / W1 / H1;

        float sum = 0;

        for (int kh = 0; kh < KH; kh++) {
            const int h2 = (h1 + PH - kh) / SH;
            if ((h1 + PH - kh) % SH != 0 || h2 < 0 || h2 >= H2) continue;

            for (int kw = 0; kw < KW; kw++) {
                const int w2 = (w1 + PW - kw) / SW;
                if ((w1 + PW - kw) % SW != 0 || w2 < 0 || w2 >= W2) continue;

                sum += col[((((n * H2 + h2) * W2 + w2) * KH + kh) * KW + kw) * C1 + c1];
            }
        }

        im[gid] = sum;
    }
}
"""


@WebGPUDescriptorGenerator.register_handler(Col2Im)
def col2im(op: Col2Im, memory_layout: MemoryLayout) -> List[Kernel]:
    col = op.inputs["col"]
    im = op.outputs["im"]

    assert col.order == Order([Axis.N, Axis.H, Axis.W, Axis.KH, Axis.KW, Axis.C])
    assert im.order == OrderNHWC

    buffer_injector = BufferInjector()
    buffer_injector.register({
        "col2im_im": memory_layout[im],
        "col2im_col": memory_layout[col],
        "col2im_N": col.shape_dict[Axis.N],
        "col2im_H2": col.shape_dict[Axis.H],
        "col2im_W2": col.shape_dict[Axis.W],
        "col2im_C1": im.shape_dict[Axis.C],
        "col2im_H1": im.shape_dict[Axis.H],
        "col2im_W1": im.shape_dict[Axis.W],
        "col2im_KH": op.KH,
        "col2im_KW": op.KW,
        "col2im_SH": op.SH,
        "col2im_SW": op.SW,
        "col2im_PH": op.PH,
        "col2im_PW": op.PW,
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
