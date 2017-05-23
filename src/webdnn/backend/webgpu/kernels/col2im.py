from typing import List

from webdnn.backend.webgpu.allocator import MemoryLayout
from webdnn.backend.webgpu.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgpu.injectors.meta_injector import MetaInjector
from webdnn.backend.webgpu.kernel import GPUSize, Kernel
from webdnn.backend.webgpu.operators.col2im import Col2Im
from webdnn.graph.axis import Axis
from webdnn.graph.order import OrderNHWC

# NOTE
#
# C1, H1, W1などはすべてConvのinput, Deconvのoutputのサイズを表すために使用
# C2, H2, W2などはすべてDeconvのinput, Convのoutputのサイズを表すために使用

template = """
kernel void %%FUNC_NAME%%(const device float *param_buffer[[buffer(0)]],
                          device float *data_buffer[[buffer(1)]],
                          const device int * %%META_NAME%% [[buffer(2)]],
                          uint index[[thread_position_in_grid]],
                          uint num_threads[[threads_per_grid]])
{
    const device float *col = data_buffer + %%META_LOAD(col2im_col_offset)%%;
    device float *im = data_buffer + %%META_LOAD(col2im_im_offset)%%;

    const int N = %%META_LOAD(col2im_N)%%;
    const int C1 = %%META_LOAD(col2im_C1)%%;
    const int H1 = %%META_LOAD(col2im_H1)%%;
    const int W1 = %%META_LOAD(col2im_W1)%%;
    const int H2 = %%META_LOAD(col2im_H2)%%;
    const int W2 = %%META_LOAD(col2im_W2)%%;
    const int KH = %%META_LOAD(col2im_KH)%%;
    const int KW = %%META_LOAD(col2im_KW)%%;
    const int SH = %%META_LOAD(col2im_SH)%%;
    const int SW = %%META_LOAD(col2im_SW)%%;
    const int PH = %%META_LOAD(col2im_PH)%%;
    const int PW = %%META_LOAD(col2im_PW)%%;

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


# noinspection PyUnusedLocal
def col2im(op: Col2Im,
           constants_layout: MemoryLayout,
           variables_layout: MemoryLayout) -> List[Kernel]:
    col = variables_layout[op.inputs["col"]]
    im = variables_layout[op.outputs["im"]]

    assert col.variable.order == OrderNHWC
    assert im.variable.order == OrderNHWC

    meta_injector = MetaInjector()
    meta_injector.register({
        "col2im_im_offset": im.offset,
        "col2im_col_offset": col.offset,
        "col2im_N": col.variable.shape_dict[Axis.N],
        "col2im_H2": col.variable.shape_dict[Axis.H],
        "col2im_W2": col.variable.shape_dict[Axis.W],
        "col2im_C1": im.variable.shape_dict[Axis.C],
        "col2im_H1": im.variable.shape_dict[Axis.H],
        "col2im_W1": im.variable.shape_dict[Axis.W],
        "col2im_KH": op.KH,
        "col2im_KW": op.KW,
        "col2im_SH": op.SH,
        "col2im_SW": op.SW,
        "col2im_PH": op.PH,
        "col2im_PW": op.PW,
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
        meta_injector.buffer
    )

    return [kernel]
