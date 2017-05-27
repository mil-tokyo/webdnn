from typing import List

from webdnn.backend.webgpu.allocator import MemoryLayout
from webdnn.backend.webgpu.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgpu.injectors.meta_injector import MetaInjector
from webdnn.backend.webgpu.kernel import GPUSize, Kernel
from webdnn.backend.webgpu.operators.im2col import Im2Col
from webdnn.graph.axis import Axis
from webdnn.graph.order import OrderNHWC, OrderCNHW


def generate_template_NHWC(SH, SW, C1):
    return """
kernel void %%FUNC_NAME%%(const device float *param_buffer[[buffer(0)]],
                          device float *data_buffer[[buffer(1)]],
                          const device int * %%META_NAME%% [[buffer(2)]],
                          ushort index_thread[[thread_position_in_threadgroup]],
                          ushort index_group[[threadgroup_position_in_grid]])
{
#define SH_EQUAL_1 %%SH_EQUAL_1%%
#define SW_EQUAL_1 %%SW_EQUAL_1%%
#define C1_DIVIDABLE_BY_4 %%C1_DIVIDABLE_BY_4%%


#if OPTIMIZE && C1_DIVIDABLE_BY_4
    const device float4 *im4 = (const device float4 *)(data_buffer + %%META_LOAD(im2col_im_offset)%%);
    device float4 *col4 = (device float4 *)(data_buffer + %%META_LOAD(im2col_col_offset)%%);
    const int C1_4 = (%%META_LOAD(im2col_C1)%%) >> 2;
#else
    const device float *im = data_buffer + %%META_LOAD(im2col_im_offset)%%;
    device float *col = data_buffer + %%META_LOAD(im2col_col_offset)%%;
    const int C1 = %%META_LOAD(im2col_C1)%%;
#endif

    // const int N = %%META_LOAD(im2col_N)%%;
    const int H1 = %%META_LOAD(im2col_H1)%%;
    const int W1 = %%META_LOAD(im2col_W1)%%;
    const int H2 = %%META_LOAD(im2col_H2)%%;
    const int W2 = %%META_LOAD(im2col_W2)%%;
    const int KH = %%META_LOAD(im2col_KH)%%;
    const int KW = %%META_LOAD(im2col_KW)%%;
    const int PH = %%META_LOAD(im2col_PH)%%;
    const int PW = %%META_LOAD(im2col_PW)%%;

#if !OPTIMIZE || !SH_EQUAL_1
    const int SH = %%META_LOAD(im2col_SH)%%;
#endif

#if !OPTIMIZE || !SW_EQUAL_1
    const int SW = %%META_LOAD(im2col_SW)%%;
#endif

    const int H1P = H1 + 2 * PH;
    const int W1P = W1 + 2 * PW;

    const int w1 = (index_group % W1P) - PW;
    const int h1 = (index_group / W1P % H1P) - PH;
    const int  n = index_group / W1P / H1P;

#if OPTIMIZE && C1_DIVIDABLE_BY_4
    for (int c1_4 = index_thread; c1_4 < C1_4; c1_4 += 64) {
        const float4 v4 = (h1 < 0 || h1 >= H1 || w1 < 0 || w1 >= W1) ? 0 : im4[((n * H1 + h1) * W1 + w1) * C1_4 + c1_4];
#else
    for (int c1 = index_thread; c1 < C1; c1 += 64) {
        const float v = (h1 < 0 || h1 >= H1 || w1 < 0 || w1 >= W1) ? 0 : im[((n * H1 + h1) * W1 + w1) * C1 + c1];
#endif

#if OPTIMIZE && SH_EQUAL_1
        for (int kh = 0; kh < KH; kh++) {
            const int h2 = h1 + PH - kh;
#else
        for (int kh = (h1 + PH) % SH; kh < KH; kh += SH) {
            const int h2 = (h1 + PH - kh) / SH;
#endif
            if (h2 < 0 || h2 >= H2) continue;

#if OPTIMIZE && SH_EQUAL_1
            for (int kw = 0; kw < KW; kw++) {
                const int w2 = w1 + PW - kw;
#else
            for (int kw = (w1 + PW) % SW; kw < KW; kw += SW) {
                const int w2 = (w1 + PW - kw) / SW;
#endif
                if (w2 < 0 || w2 >= W2) continue;

#if OPTIMIZE && C1_DIVIDABLE_BY_4
                col4[((((n * H2 + h2) * W2 + w2) * KH + kh) * KW + kw) * C1_4 + c1_4] = v4;
#else
                col[((((n * H2 + h2) * W2 + w2) * KH + kh) * KW + kw) * C1 + c1] = v;
#endif
            }
        }
    }


#undef SH_EQUAL_1
#undef SW_EQUAL_1
#undef C1_DIVIDABLE_BY_4
}
""" \
        .replace("%%SH_EQUAL_1%%", "1" if SH == 1 else "0") \
        .replace("%%SW_EQUAL_1%%", "1" if SW == 1 else "0") \
        .replace("%%C1_DIVIDABLE_BY_4%%", "1" if C1 % 4 == 0 else "0")


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


def im2col(op: Im2Col,
           constants_layout: MemoryLayout,
           variables_layout: MemoryLayout) -> List[Kernel]:
    im = variables_layout[op.inputs["im"]]
    col = variables_layout[op.outputs["col"]]

    assert im.variable.order == OrderNHWC
    assert col.variable.order == OrderNHWC or col.variable.order == OrderCNHW

    N = im.variable.shape_dict[Axis.N]
    C1 = im.variable.shape_dict[Axis.C]
    H1 = im.variable.shape_dict[Axis.H]
    W1 = im.variable.shape_dict[Axis.W]

    H1P = H1 + 2 * op.PH
    W1P = W1 + 2 * op.PW

    meta_injector = MetaInjector()
    meta_injector.register({
        "im2col_im_offset": im.offset,
        "im2col_col_offset": col.offset,
        "im2col_N": col.variable.shape_dict[Axis.N],
        "im2col_C1": C1,
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

    name_injector = KernelNameInjector(op)

    source = template_CNHW if col.variable.order == OrderCNHW else generate_template_NHWC(op.SH, op.SW, C1)
    source = meta_injector.inject(source)
    source = name_injector.inject(source)

    kernel = Kernel(
        {name_injector.name: source},
        name_injector.name,
        GPUSize(N * H1P * W1P, 1, 1),
        GPUSize(64, 1, 1),
        meta_injector.buffer
    )

    return [kernel]
