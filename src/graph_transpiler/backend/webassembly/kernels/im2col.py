from typing import List

from graph_transpiler.backend.webassembly.kernel import Kernel
from graph_transpiler.backend.webassembly.kernels import util
from graph_transpiler.backend.webassembly.meta_buffer_injector import MetaBufferInjector
from graph_transpiler.backend.webassembly.operators.im2col import Im2Col
from graph_transpiler.backend.webgpu.allocator import MemoryLayout
from graph_transpiler.graph.axis import Axis
from graph_transpiler.graph.variables.attributes.order import OrderNHWC, OrderCNHW

template_NHWC = """
void %%FUNC_NAME%%(const int * %%META_NAME%%)
{
    const float *im = data_buffer + %%META_LOAD(im2col_im_offset)%%;
    float *col = data_buffer + %%META_LOAD(im2col_col_offset)%%;

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

    for (int gid = 0; gid < N*H2*W2*KH*KW*C1; gid += 1) {
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
void %%FUNC_NAME%%(const int * %%META_NAME%%)
{
    const float *im = data_buffer + %%META_LOAD(im2col_im_offset)%%;
    float *col = data_buffer + %%META_LOAD(im2col_col_offset)%%;

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

    for (int gid = 0; gid < N*H2*W2*KH*KW*C1; gid += 1) {
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

    source = template_CNHW if col.variable.order == OrderCNHW else template_NHWC
    source = metabuffer_injector.inject(source)
    func_name = util.add_canonical_suffix("im2col", source)
    source = source.replace("%%FUNC_NAME%%", func_name)

    kernel = Kernel(
        {func_name: source},
        func_name,
        metabuffer_injector.generate_buffer()
    )

    return [kernel]
