from typing import List

from graph_builder.backend.webgpu.allocator import MemoryLayout
from graph_builder.backend.webgpu.kernel import GPUSize, Kernel
from graph_builder.backend.webgpu.kernels import util
from graph_builder.backend.webgpu.meta_buffer_injector import MetaBufferInjector
from graph_builder.backend.webgpu.operators.im2col import Im2Col
from graph_builder.graph.axis import Axis
from graph_builder.graph.variables.attributes.order import OrderNHWC, OrderCNHW

template_NHWC = """
kernel void %%FUNC_NAME%%(const device float *param_buffer[[buffer(0)]],
                          device float *data_buffer[[buffer(1)]],
                          const device int * %%META_NAME%% [[buffer(2)]],
                          uint index[[thread_position_in_grid]],
                          uint num_threads[[threads_per_grid]])
{
    const device float *im = data_buffer + %%META_LOAD(im2col_im_offset)%%;
    device float *col = data_buffer + %%META_LOAD(im2col_col_offset)%%;

    const int N = %%META_LOAD(im2col_N)%%;
    const int C1 = %%META_LOAD(im2col_C1)%%;
    const int H1 = %%META_LOAD(im2col_H1)%%;
    const int W1 = %%META_LOAD(im2col_W1)%%;
    const int H2 = %%META_LOAD(im2col_H2)%%;
    const int W2 = %%META_LOAD(im2col_W2)%%;
    const int KH = %%META_LOAD(im2col_KH)%%;
    const int KW = %%META_LOAD(im2col_KW)%%;
    const int SH = %%META_LOAD(im2col_SH)%%;
    const int SW = %%META_LOAD(im2col_SW)%%;
    const int PH = %%META_LOAD(im2col_PH)%%;
    const int PW = %%META_LOAD(im2col_PW)%%;

    for (int gid = index; gid < N*H2*W2*KH*KW*C1; gid += num_threads) {
        const int c1 = gid % C1;
        const int kw = gid / C1 % KW;
        const int kh = gid / C1 / KW % KH;
        const int w2 = gid / C1 / KW / KH % W2;
        const int h2 = gid / C1 / KW / KH / W2 % H2;
        const int  n = gid / C1 / KW / KH / W2 / H2;
        
        const int h1 = h2 * SH - PH + kh;
        const int w1 = w2 * SW - PW + kw;

        col[gid] = (h1 < 0 || h1 >= H1 || w1 < 0 || w1 >= W1) ? 0 : im[((n*H1+h1)*W1+w1)*C1+c1];
    }
}
"""

template_CNHW = """
kernel void %%FUNC_NAME%%(const device float *param_buffer[[buffer(0)]],
                          device float *data_buffer[[buffer(1)]],
                          const device int * %%META_NAME%% [[buffer(2)]],
                          uint index[[thread_position_in_grid]],
                          uint num_threads[[threads_per_grid]])
{
    const device float *im = data_buffer + %%META_LOAD(im2col_im_offset)%%;
    device float *col = data_buffer + %%META_LOAD(im2col_col_offset)%%;

    const int N = %%META_LOAD(im2col_N)%%;
    const int C1 = %%META_LOAD(im2col_C1)%%;
    const int H1 = %%META_LOAD(im2col_H1)%%;
    const int W1 = %%META_LOAD(im2col_W1)%%;
    const int H2 = %%META_LOAD(im2col_H2)%%;
    const int W2 = %%META_LOAD(im2col_W2)%%;
    const int KH = %%META_LOAD(im2col_KH)%%;
    const int KW = %%META_LOAD(im2col_KW)%%;
    const int SH = %%META_LOAD(im2col_SH)%%;
    const int SW = %%META_LOAD(im2col_SW)%%;
    const int PH = %%META_LOAD(im2col_PH)%%;
    const int PW = %%META_LOAD(im2col_PW)%%;

    for (int gid = index; gid < N*H2*W2*KH*KW*C1; gid += num_threads) {
        const int w2 = gid % W2;
        const int h2 = gid / W2 % H2;
        const int  n = gid / W2 / H2 % N;
        const int c1 = gid / W2 / H2 / N % C1;
        const int kw = gid / W2 / H2 / N / C1 % KW;
        const int kh = gid / W2 / H2 / N / C1 / KW;

        const int h1 = h2 * SH - PH + kh;
        const int w1 = w2 * SW - PW + kw;

        col[gid] = (h1 < 0 || h1 >= H1 || w1 < 0 || w1 >= W1) ? 0 : im[((n*H1+h1)*W1+w1)*C1+c1];
    }
}
"""


# noinspection PyUnusedLocal
def im2col(op: Im2Col,
           constants_layout: MemoryLayout,
           variables_layout: MemoryLayout,
           metabuffer_injector: MetaBufferInjector = None) -> List[Kernel]:
    im = variables_layout[op.inputs["im"]]
    col = variables_layout[op.outputs["col"]]

    assert im.variable.axis_order == OrderNHWC
    assert col.variable.axis_order == OrderNHWC or col.variable.axis_order == OrderCNHW

    if metabuffer_injector is None:
        metabuffer_injector = MetaBufferInjector()

    metabuffer_injector.register({
        "im2col_im_offset": im.offset,
        "im2col_col_offset": col.offset,
        "im2col_N": col.variable.shape_dict[Axis.N],
        "im2col_C1": im.variable.shape_dict[Axis.C],
        "im2col_H1": im.variable.shape_dict[Axis.H],
        "im2col_W1": im.variable.shape_dict[Axis.W],
        "im2col_H2": col.variable.shape_dict[Axis.H],
        "im2col_W2": col.variable.shape_dict[Axis.W],
        "im2col_KH": op.KH,
        "im2col_KW": op.KW,
        "im2col_SH": op.SH,
        "im2col_SW": op.SW,
        "im2col_PH": op.PH,
        "im2col_PW": op.PW,
    })

    source = template_CNHW if col.variable.axis_order == OrderCNHW else template_NHWC
    source = metabuffer_injector.inject(source)
    func_name = util.add_canonical_suffix("im2col", source)
    source = source.replace("%%FUNC_NAME%%", func_name)

    kernel = Kernel(
        {func_name: source},
        func_name,
        GPUSize(8, 1, 1),
        GPUSize(1024, 1, 1),
        metabuffer_injector.generate_buffer()
    )

    return [kernel]
