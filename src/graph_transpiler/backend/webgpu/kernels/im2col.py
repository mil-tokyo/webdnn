from typing import List

from graph_transpiler.backend.webgpu.allocator import MemoryLayout
from graph_transpiler.backend.webgpu.kernel import GPUSize, Kernel
from graph_transpiler.backend.webgpu.kernels import util
from graph_transpiler.backend.webgpu.meta_buffer_injector import MetaBufferInjector
from graph_transpiler.backend.webgpu.operators.im2col import Im2Col
from graph_transpiler.graph.axis import Axis
from graph_transpiler.graph.variables.attributes.order import OrderNHWC, OrderCNHW


def generate_template_NHWC():
    return """
kernel void %%FUNC_NAME%%(const device float *param_buffer[[buffer(0)]],
                          device float *data_buffer[[buffer(1)]],
                          const device int * %%META_NAME%% [[buffer(2)]],
                          ushort index_thread[[thread_position_in_threadgroup]],
                          ushort index_group[[threadgroup_position_in_grid]])
{
    const device float *im = data_buffer + %%META_LOAD(im2col_im_offset)%%;
    device float *col = data_buffer + %%META_LOAD(im2col_col_offset)%%;

    // const int N = %%META_LOAD(im2col_N)%%;
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

    const int H1P = H1 + 2 * PH;
    const int W1P = W1 + 2 * PW;

    const int w1 = (index_group % W1P) - PW;
    const int h1 = (index_group / W1P % H1P) - PH;
    const int  n = index_group / W1P / H1P;

    for (int c1 = index_thread; c1 < C1; c1 += 64) {
        const float v = (h1 < 0 || h1 >= H1 || w1 < 0 || w1 >= W1) ? 0 : im[((n * H1 + h1) * W1 + w1) * C1 + c1];

        for (int kh = (h1 + PH) % %%UNIT_KH%%; kh < KH; kh += SH) {
            const int h2 = (h1 + PH - kh) / SH;
            if (h2 < 0 || h2 >= H2) continue;

            for (int kw = (w1 + PW) % %%UNIT_KW%%; kw < KW; kw += SW) {
                const int w2 = (w1 + PW - kw) / SW;
                if (w2 < 0 || w2 >= W2) continue;

                col[((((n * H2 + h2) * W2 + w2) * KH + kh) * KW + kw) * C1 + c1] = v;
            }
        }
    }
}
""" \
        .replace("%%UNIT_KH%%", "SH") \
        .replace("%%UNIT_KW%%", "SW")


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

    assert im.variable.order == OrderNHWC
    assert col.variable.order == OrderNHWC or col.variable.order == OrderCNHW

    if metabuffer_injector is None:
        metabuffer_injector = MetaBufferInjector()

    N = im.variable.shape_dict[Axis.N]
    C1 = im.variable.shape_dict[Axis.C]
    H1 = im.variable.shape_dict[Axis.H]
    W1 = im.variable.shape_dict[Axis.W]

    H1P = H1 + 2 * op.PH
    W1P = W1 + 2 * op.PW

    metabuffer_injector.register({
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

    if col.variable.order == OrderCNHW:
        source = template_CNHW

    else:
        source = generate_template_NHWC()

    source = metabuffer_injector.inject(source)
    func_name = util.add_canonical_suffix("im2col", source)
    source = source.replace("%%FUNC_NAME%%", func_name)

    kernel = Kernel(
        {func_name: source},
        func_name,
        GPUSize(N * H1P * W1P, 1, 1),
        GPUSize(64, 1, 1),
        metabuffer_injector.generate_buffer()
    )

    return [kernel]
